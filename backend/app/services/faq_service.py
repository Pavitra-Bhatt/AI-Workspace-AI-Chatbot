from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.faq import FAQ, FAQCategory, FAQStatus
import numpy as np
import logging

logger = logging.getLogger(__name__)


class FAQService:
    def __init__(self):
        self.ai_service = None  # Will be set later to avoid circular import
    
    def set_ai_service(self, ai_service):
        """Set the AI service after initialization to avoid circular imports"""
        self.ai_service = ai_service
    
    async def create_faq(
        self, 
        db: AsyncSession, 
        faq_data: Dict[str, Any]
    ) -> FAQ:
        """Create a new FAQ entry"""
        try:
            # Generate embeddings for question and answer if AI service is available
            if self.ai_service:
                question_embedding = await self.ai_service.generate_embeddings(faq_data["question"])
                answer_embedding = await self.ai_service.generate_embeddings(faq_data["answer"])
            else:
                question_embedding = None
                answer_embedding = None
            
            faq = FAQ(
                question=faq_data["question"],
                answer=faq_data["answer"],
                category_id=faq_data["category_id"],
                keywords=faq_data.get("keywords", []),
                priority=faq_data.get("priority", 0),
                language=faq_data.get("language", "en"),
                meta_title=faq_data.get("meta_title"),
                meta_description=faq_data.get("meta_description"),
                slug=faq_data.get("slug"),
                question_embedding=question_embedding,
                answer_embedding=answer_embedding,
                status=FAQStatus.DRAFT
            )
            
            db.add(faq)
            await db.commit()
            await db.refresh(faq)
            
            return faq
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create FAQ: {e}")
            raise
    
    async def update_faq(
        self, 
        db: AsyncSession, 
        faq_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[FAQ]:
        """Update an existing FAQ entry"""
        try:
            result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
            faq = result.scalar_one_or_none()
            
            if not faq:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(faq, field):
                    setattr(faq, field, value)
            
            # Regenerate embeddings if question or answer changed
            if ("question" in update_data or "answer" in update_data) and self.ai_service:
                question_embedding = await self.ai_service.generate_embeddings(faq.question)
                answer_embedding = await self.ai_service.generate_embeddings(faq.answer)
                faq.question_embedding = question_embedding
                faq.answer_embedding = answer_embedding
            
            await db.commit()
            await db.refresh(faq)
            
            return faq
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update FAQ: {e}")
            raise
    
    async def search_semantic(
        self, 
        query: str, 
        limit: int = 5,
        category_id: Optional[int] = None,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search FAQs using semantic similarity"""
        try:
            # Generate embedding for query if AI service is available
            if self.ai_service:
                query_embedding = await self.ai_service.generate_embeddings(query)
            else:
                # Fallback to text search if no AI service
                return await self.search_text(query, limit, category_id, language)
            
            if not query_embedding:
                return []
            
            # Get all published FAQs
            query = select(FAQ).where(
                FAQ.status == FAQStatus.PUBLISHED,
                FAQ.language == language
            )
            
            if category_id:
                query = query.where(FAQ.category_id == category_id)
            
            result = await db.execute(query)
            faqs = result.scalars().all()
            
            # Calculate similarities
            similarities = []
            for faq in faqs:
                if faq.question_embedding:
                    # Calculate cosine similarity
                    question_sim = self._cosine_similarity(query_embedding, faq.question_embedding)
                    answer_sim = self._cosine_similarity(query_embedding, faq.answer_embedding)
                    
                    # Use the higher similarity score
                    max_sim = max(question_sim, answer_sim)
                    
                    similarities.append({
                        "faq": faq,
                        "similarity": max_sim
                    })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            return [
                {
                    "id": item["faq"].id,
                    "question": item["faq"].question,
                    "answer": item["faq"].answer,
                    "category_id": item["faq"].category_id,
                    "similarity": item["similarity"]
                }
                for item in similarities[:limit]
            ]
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
    
    async def search_text(
        self, 
        query: str, 
        limit: int = 10,
        category_id: Optional[int] = None,
        language: str = "en"
    ) -> List[FAQ]:
        """Search FAQs using text search"""
        try:
            search_query = select(FAQ).where(
                FAQ.status == FAQStatus.PUBLISHED,
                FAQ.language == language,
                func.lower(FAQ.question).contains(query.lower())
            )
            
            if category_id:
                search_query = search_query.where(FAQ.category_id == category_id)
            
            result = await db.execute(search_query)
            return result.scalars().limit(limit).all()
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    async def get_faq_by_id(self, db: AsyncSession, faq_id: int) -> Optional[FAQ]:
        """Get FAQ by ID"""
        result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
        return result.scalar_one_or_none()
    
    async def get_faqs_by_category(
        self, 
        db: AsyncSession, 
        category_id: int,
        limit: int = 50
    ) -> List[FAQ]:
        """Get FAQs by category"""
        result = await db.execute(
            select(FAQ)
            .where(FAQ.category_id == category_id, FAQ.status == FAQStatus.PUBLISHED)
            .order_by(FAQ.priority.desc(), FAQ.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def increment_view_count(self, db: AsyncSession, faq_id: int):
        """Increment FAQ view count"""
        try:
            result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
            faq = result.scalar_one_or_none()
            
            if faq:
                faq.view_count += 1
                await db.commit()
                
        except Exception as e:
            logger.error(f"Failed to increment view count: {e}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0 