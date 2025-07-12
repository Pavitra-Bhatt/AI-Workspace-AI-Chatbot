from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class MessageType(str, enum.Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"


class MessageStatus(str, enum.Enum):
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    language = Column(String(10), default="en")
    
    # Conversation metadata
    context = Column(JSON)  # Store conversation context, user preferences, etc.
    tags = Column(JSON)  # Store conversation tags for categorization
    
    # Analytics
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title='{self.title}')>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    
    # AI-specific fields
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(100))
    response_time_ms = Column(Integer)
    
    # Metadata
    message_metadata = Column(JSON)  # Store additional data like intent, confidence, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    delivered_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    user = relationship("User")
    
    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, type='{self.message_type}')>" 