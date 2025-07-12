from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


class AuditAction(str, enum.Enum):
    # User actions
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_REGISTER = "user_register"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # Data access
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    
    # GDPR actions
    CONSENT_GIVEN = "consent_given"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_RETENTION = "data_retention"
    
    # Admin actions
    ADMIN_LOGIN = "admin_login"
    FAQ_CREATE = "faq_create"
    FAQ_UPDATE = "faq_update"
    FAQ_DELETE = "faq_delete"
    
    # System actions
    SYSTEM_ERROR = "system_error"
    SECURITY_ALERT = "security_alert"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(100))  # user, conversation, faq, etc.
    resource_id = Column(String(100))  # ID of the affected resource
    
    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)
    session_id = Column(String(255))
    
    # Details
    description = Column(Text)
    details = Column(JSON)  # Store additional context data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>" 