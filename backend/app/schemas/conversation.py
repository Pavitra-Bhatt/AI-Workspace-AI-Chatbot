from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.conversation import MessageType, MessageStatus


class ConversationBase(BaseModel):
    title: Optional[str] = None
    language: str = "en"
    context: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    is_archived: Optional[bool] = None
    tags: Optional[List[str]] = None


class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    message_count: int
    total_tokens: int
    duration_seconds: int
    is_active: bool
    is_archived: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str
    message_type: MessageType
    metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    conversation_id: int


class MessageUpdate(BaseModel):
    status: Optional[MessageStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    user_id: int
    status: MessageStatus
    tokens_used: int
    model_used: Optional[str] = None
    response_time_ms: Optional[int] = None
    created_at: datetime
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    language: str = "en"
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    message: MessageResponse
    conversation: ConversationResponse
    suggested_questions: Optional[List[str]] = None
    related_faqs: Optional[List[Dict[str, Any]]] = None


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    page: int
    size: int 