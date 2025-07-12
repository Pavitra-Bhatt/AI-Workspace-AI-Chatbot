import openai
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import logging
import numpy as np
from transformers import AutoTokenizer, AutoModel, pipeline

# Try to import sentence_transformers, fallback if not available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from app.config import settings
from app.models.conversation import MessageType
from app.services.faq_service import FAQService

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.faq_service = FAQService()
        self.ai_provider = settings.AI_PROVIDER
        
        # Set the AI service in FAQ service to avoid circular imports
        self.faq_service.set_ai_service(self)
        
        # Initialize local models
        if self.ai_provider == "local":
            self._initialize_local_models()
        elif self.ai_provider == "openai":
            import openai
            openai.api_key = settings.OPENAI_API_KEY
        elif self.ai_provider == "huggingface":
            self._initialize_huggingface_models()
    
    def _initialize_local_models(self):
        """Initialize local models for free AI processing"""
        try:
            # Initialize embedding model if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer(settings.LOCAL_EMBEDDING_MODEL)
            else:
                self.embedding_model = None
                logger.warning("sentence_transformers not available, using fallback embeddings")
            
            # Initialize chat model
            self.tokenizer = AutoTokenizer.from_pretrained(settings.LOCAL_CHAT_MODEL)
            self.chat_model = AutoModel.from_pretrained(settings.LOCAL_CHAT_MODEL)
            
            # Initialize text generation pipeline
            self.text_generator = pipeline(
                "text-generation",
                model=settings.LOCAL_CHAT_MODEL,
                tokenizer=self.tokenizer,
                max_length=100,
                do_sample=True,
                temperature=0.7
            )
            
            logger.info("Local AI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize local models: {e}")
            # Fallback to simple response generation
            self.embedding_model = None
            self.text_generator = None
    
    def _initialize_huggingface_models(self):
        """Initialize HuggingFace models (free tier)"""
        try:
            from huggingface_hub import login
            if settings.HUGGINGFACE_API_KEY:
                login(settings.HUGGINGFACE_API_KEY)
            
            # Use smaller, free models if available
            if SENTENCE_TRANSFORMERS_AVAILABLE:
                self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            else:
                self.embedding_model = None
                logger.warning("sentence_transformers not available, using fallback embeddings")
            
            self.text_generator = pipeline("text-generation", model="gpt2")
            
            logger.info("HuggingFace models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace models: {e}")
            self._initialize_local_models()
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: List[Dict[str, Any]] = None,
        user_context: Dict[str, Any] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate AI response using free models"""
        start_time = time.time()
        
        try:
            # Get relevant FAQs
            relevant_faqs = await self.faq_service.search_semantic(message, limit=3)
            
            # Generate response based on provider
            if self.ai_provider == "local":
                response = self._generate_local_response(message, conversation_history, relevant_faqs)
            elif self.ai_provider == "openai":
                response = await self._generate_openai_response(message, conversation_history, relevant_faqs)
            elif self.ai_provider == "huggingface":
                response = self._generate_huggingface_response(message, conversation_history, relevant_faqs)
            else:
                response = self._generate_fallback_response(message, relevant_faqs)
            
            # Calculate metrics
            response_time = int((time.time() - start_time) * 1000)
            
            return {
                "content": response,
                "tokens_used": len(message.split()),  # Rough estimation
                "prompt_tokens": len(message.split()),
                "completion_tokens": len(response.split()),
                "model_used": f"{self.ai_provider}-local",
                "response_time_ms": response_time,
                "relevant_faqs": relevant_faqs
            }
            
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
                "tokens_used": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "model_used": f"{self.ai_provider}-fallback",
                "response_time_ms": int((time.time() - start_time) * 1000),
                "error": str(e)
            }
    
    def _generate_local_response(self, message: str, conversation_history: List[Dict[str, Any]], relevant_faqs: List[Dict[str, Any]]) -> str:
        """Generate response using local models"""
        try:
            # Build context from conversation history
            context = self._build_context(message, conversation_history, relevant_faqs)
            
            # Generate response using local model
            if self.text_generator:
                inputs = self.tokenizer.encode(context, return_tensors="pt", max_length=512, truncation=True)
                outputs = self.chat_model.generate(inputs, max_length=100, do_sample=True, temperature=0.7)
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Clean up response
                response = response.replace(context, "").strip()
                if not response:
                    response = self._generate_simple_response(message, relevant_faqs)
            else:
                response = self._generate_simple_response(message, relevant_faqs)
            
            return response
            
        except Exception as e:
            logger.error(f"Local response generation failed: {e}")
            return self._generate_simple_response(message, relevant_faqs)
    
    def _generate_huggingface_response(self, message: str, conversation_history: List[Dict[str, Any]], relevant_faqs: List[Dict[str, Any]]) -> str:
        """Generate response using HuggingFace models"""
        try:
            context = self._build_context(message, conversation_history, relevant_faqs)
            
            if self.text_generator:
                response = self.text_generator(context, max_length=100, do_sample=True)[0]['generated_text']
                response = response.replace(context, "").strip()
                if not response:
                    response = self._generate_simple_response(message, relevant_faqs)
            else:
                response = self._generate_simple_response(message, relevant_faqs)
            
            return response
            
        except Exception as e:
            logger.error(f"HuggingFace response generation failed: {e}")
            return self._generate_simple_response(message, relevant_faqs)
    
    async def _generate_openai_response(self, message: str, conversation_history: List[Dict[str, Any]], relevant_faqs: List[Dict[str, Any]]) -> str:
        """Generate response using OpenAI (if API key is provided)"""
        try:
            import openai
            
            messages = self._build_conversation_context(message, conversation_history, relevant_faqs)
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",  # Use cheaper model
                messages=messages,
                max_tokens=100,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI response generation failed: {e}")
            return self._generate_simple_response(message, relevant_faqs)
    
    def _generate_simple_response(self, message: str, relevant_faqs: List[Dict[str, Any]]) -> str:
        """Generate simple response when AI models are not available"""
        # Simple rule-based responses
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! How can I help you today?"
        elif "help" in message_lower:
            return "I'm here to help! What would you like to know?"
        elif "thank" in message_lower:
            return "You're welcome! Is there anything else I can help you with?"
        elif relevant_faqs:
            # Use relevant FAQ if available
            best_faq = relevant_faqs[0]
            default_answer = "I don't have a specific answer for that."
            return f"Based on your question, here's what I found: {best_faq.get('answer', default_answer)}"
        else:
            return "I understand your question. Let me help you find the information you need. Could you please provide more details?"
    
    def _build_context(self, message: str, conversation_history: List[Dict[str, Any]], relevant_faqs: List[Dict[str, Any]]) -> str:
        """Build context for AI response"""
        context_parts = []
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = "User" if msg.get("message_type") == "user" else "Assistant"
                context_parts.append(f"{role}: {msg.get('content', '')}")
        
        # Add relevant FAQs
        if relevant_faqs:
            faq_context = "Relevant information:\n"
            for faq in relevant_faqs[:2]:  # Top 2 FAQs
                faq_context += f"Q: {faq.get('question', '')}\nA: {faq.get('answer', '')}\n"
            context_parts.append(faq_context)
        
        # Add current message
        context_parts.append(f"User: {message}")
        context_parts.append("Assistant:")
        
        return "\n".join(context_parts)
    
    def _build_conversation_context(self, message: str, conversation_history: List[Dict[str, Any]], relevant_faqs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Build conversation context for OpenAI"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Provide concise and helpful responses."
            }
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = "user" if msg.get("message_type") == "user" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg.get("content", "")
                })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": message
        })
        
        return messages
    
    async def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings using local models"""
        try:
            if self.embedding_model and SENTENCE_TRANSFORMERS_AVAILABLE:
                embeddings = self.embedding_model.encode(text)
                return embeddings.tolist()
            else:
                # Simple fallback embedding
                return self._simple_embedding(text)
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """Simple fallback embedding using basic text features"""
        # Convert text to simple numerical features
        words = text.lower().split()
        word_count = len(words)
        char_count = len(text)
        
        # Create a simple feature vector
        features = [
            word_count / 100.0,  # Normalized word count
            char_count / 500.0,  # Normalized character count
            len(set(words)) / max(word_count, 1),  # Vocabulary diversity
            sum(len(word) for word in words) / max(word_count, 1),  # Average word length
        ]
        
        # Pad to 384 dimensions (common embedding size)
        while len(features) < 384:
            features.append(0.0)
        
        return features[:384]
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Simple content moderation (free alternative)"""
        # Basic keyword-based moderation
        inappropriate_keywords = [
            "hate", "violence", "abuse", "discrimination", "harassment"
        ]
        
        text_lower = text.lower()
        flagged = any(keyword in text_lower for keyword in inappropriate_keywords)
        
        return {
            "flagged": flagged,
            "categories": {"inappropriate": flagged},
            "category_scores": {"inappropriate": 0.8 if flagged else 0.1}
        } 