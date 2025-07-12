from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.analytics import AnalyticsEventType


class AnalyticsEventCreate(BaseModel):
    event_type: AnalyticsEventType
    event_data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class AnalyticsResponse(BaseModel):
    user_id: int
    total_conversations: int
    total_messages: int
    total_tokens_used: int
    avg_messages_per_conversation: float
    avg_conversation_duration: float
    last_activity: Optional[datetime] = None


class ConversationAnalyticsResponse(BaseModel):
    conversation_id: int
    total_messages: int
    user_messages: int
    bot_messages: int
    total_tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    avg_response_time: float
    total_duration: int
    user_satisfaction_score: Optional[float] = None
    fallback_count: int
    error_count: int


class DashboardMetrics(BaseModel):
    total_users: int
    active_users_today: int
    total_conversations: int
    conversations_today: int
    total_messages: int
    messages_today: int
    avg_response_time: float
    user_satisfaction_score: float
    faq_views: int
    faq_helpful_rate: float


class TimeSeriesData(BaseModel):
    date: str
    value: int


class AnalyticsReport(BaseModel):
    period: str
    metrics: DashboardMetrics
    time_series: List[TimeSeriesData]
    top_faqs: List[Dict[str, Any]]
    top_questions: List[str]
    error_summary: List[Dict[str, Any]] 