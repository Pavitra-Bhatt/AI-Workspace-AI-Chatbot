from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message, MessageType, MessageStatus
from app.schemas.conversation import ChatRequest, ChatResponse, ConversationResponse, MessageResponse
from app.auth import get_current_user
from app.services.ai_service import AIService
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message and get AI response"""
    try:
        ai_service = AIService()
        
        # Get or create conversation
        conversation = None
        if chat_request.conversation_id:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == chat_request.conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
            conversation = result.scalar_one_or_none()
        
        if not conversation:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                language=chat_request.language,
                context=chat_request.context,
                title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            )
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
        
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            content=chat_request.message,
            message_type=MessageType.USER,
            status=MessageStatus.SENT
        )
        db.add(user_message)
        await db.commit()
        await db.refresh(user_message)
        
        # Get conversation history for context
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )
        history = result.scalars().all()
        history.reverse()
        
        # Prepare conversation history for AI
        conversation_history = []
        for msg in history:
            conversation_history.append({
                "content": msg.content,
                "message_type": msg.message_type.value,
                "created_at": msg.created_at.isoformat()
            })
        
        # Generate AI response
        ai_response = await ai_service.generate_response(
            message=chat_request.message,
            conversation_history=conversation_history,
            user_context=conversation.context,
            language=chat_request.language
        )
        
        # Save AI response
        bot_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,  # Same user_id for bot messages
            content=ai_response["content"],
            message_type=MessageType.BOT,
            status=MessageStatus.SENT,
            tokens_used=ai_response.get("tokens_used", 0),
            model_used=ai_response.get("model_used"),
            response_time_ms=ai_response.get("response_time_ms"),
            metadata={
                "prompt_tokens": ai_response.get("prompt_tokens", 0),
                "completion_tokens": ai_response.get("completion_tokens", 0),
                "relevant_faqs": ai_response.get("relevant_faqs", [])
            }
        )
        db.add(bot_message)
        
        # Update conversation metrics
        conversation.message_count += 2  # User + Bot message
        conversation.total_tokens += ai_response.get("tokens_used", 0)
        conversation.last_message_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(bot_message)
        await db.refresh(conversation)
        
        # Analytics tracking would go here in production
        # For now, we'll skip analytics to keep the app running
        
        # Prepare response
        suggested_questions = await _generate_suggested_questions(ai_response["content"])
        
        return ChatResponse(
            message=MessageResponse.from_orm(bot_message),
            conversation=ConversationResponse.from_orm(conversation),
            suggested_questions=suggested_questions,
            related_faqs=ai_response.get("relevant_faqs", [])
        )
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: AsyncSession = Depends(get_db)):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message (similar to send_message endpoint)
            # This is a simplified version - in production you'd want more robust handling
            
            # Send response back to client
            response = {
                "type": "message",
                "content": "Message received via WebSocket",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(user_id)


async def _generate_suggested_questions(bot_response: str) -> List[str]:
    """Generate suggested follow-up questions based on bot response"""
    # This is a simplified implementation
    # In production, you might use AI to generate contextual questions
    suggestions = [
        "Can you tell me more about that?",
        "What are the next steps?",
        "Is there anything else I should know?"
    ]
    return suggestions[:3] 