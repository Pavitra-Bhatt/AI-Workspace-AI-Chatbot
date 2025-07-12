from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Float, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class AnalyticsEventType(str, enum.Enum):
    USER_LOGIN = "user_login"
    CONVERSATION_START = "conversation_start"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    FAQ_VIEW = "faq_view"
    FAQ_HELPFUL = "faq_helpful"
    FAQ_NOT_HELPFUL = "faq_not_helpful"
    ERROR_OCCURRED = "error_occurred"


class UserAnalytics(Base):
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session tracking
    session_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    # Usage metrics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Time tracking
    total_session_time = Column(Integer, default=0)  # in seconds
    last_activity = Column(DateTime(timezone=True))
    
    # Engagement metrics
    avg_messages_per_conversation = Column(Float, default=0.0)
    avg_conversation_duration = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analytics")
    
    def __repr__(self):
        return f"<UserAnalytics(id={self.id}, user_id={self.user_id})>"


class ConversationAnalytics(Base):
    __tablename__ = "conversation_analytics"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message metrics
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    bot_messages = Column(Integer, default=0)
    
    # Token usage
    total_tokens_used = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    
    # Performance metrics
    avg_response_time = Column(Float, default=0.0)  # in milliseconds
    total_duration = Column(Integer, default=0)  # in seconds
    
    # Quality metrics
    user_satisfaction_score = Column(Float)  # 1-5 scale
    fallback_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ConversationAnalytics(id={self.id}, conversation_id={self.conversation_id})>"


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(String(255))
    
    # Event details
    event_type = Column(Enum(AnalyticsEventType), nullable=False)
    event_data = Column(JSON)  # Store event-specific data
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    referrer = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AnalyticsEvent(id={self.id}, event_type='{self.event_type}')>" 