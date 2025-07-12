from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class FAQStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("faq_categories.id"), nullable=False)
    
    # Content
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(JSON)  # Store keywords for better search
    
    # Vector embeddings for semantic search
    question_embedding = Column(JSON)  # Store vector embedding
    answer_embedding = Column(JSON)  # Store vector embedding
    
    # Metadata
    status = Column(Enum(FAQStatus), default=FAQStatus.DRAFT)
    priority = Column(Integer, default=0)
    language = Column(String(10), default="en")
    
    # Analytics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    
    # SEO
    slug = Column(String(255), unique=True, index=True)
    meta_title = Column(String(255))
    meta_description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    category = relationship("FAQCategory", back_populates="faqs")
    
    def __repr__(self):
        return f"<FAQ(id={self.id}, question='{self.question[:50]}...')>"


class FAQCategory(Base):
    __tablename__ = "faq_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(255), unique=True, index=True)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey("faq_categories.id"))
    
    # Display
    icon = Column(String(100))
    color = Column(String(7))  # Hex color code
    sort_order = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    faqs = relationship("FAQ", back_populates="category")
    parent = relationship("FAQCategory", remote_side=[id], back_populates="children")
    children = relationship("FAQCategory", back_populates="parent", overlaps="parent")
    
    def __repr__(self):
        return f"<FAQCategory(id={self.id}, name='{self.name}')>" 