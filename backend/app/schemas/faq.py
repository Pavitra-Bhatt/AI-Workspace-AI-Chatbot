from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.faq import FAQStatus


class FAQBase(BaseModel):
    question: str
    answer: str
    keywords: Optional[List[str]] = None
    priority: int = 0
    language: str = "en"
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class FAQCreate(FAQBase):
    category_id: int
    slug: Optional[str] = None
    
    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if not v and 'question' in values:
            # Generate slug from question
            return values['question'].lower().replace(' ', '-')[:50]
        return v


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category_id: Optional[int] = None
    keywords: Optional[List[str]] = None
    status: Optional[FAQStatus] = None
    priority: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None


class FAQResponse(FAQBase):
    id: int
    category_id: int
    slug: str
    status: FAQStatus
    view_count: int
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FAQCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0


class FAQCategoryCreate(FAQCategoryBase):
    parent_id: Optional[int] = None
    slug: Optional[str] = None
    
    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if not v and 'name' in values:
            return values['name'].lower().replace(' ', '-')
        return v


class FAQCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class FAQCategoryResponse(FAQCategoryBase):
    id: int
    parent_id: Optional[int] = None
    slug: str
    is_active: bool
    faq_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FAQSearchRequest(BaseModel):
    query: str
    category_id: Optional[int] = None
    language: str = "en"
    limit: int = 10


class FAQSearchResponse(BaseModel):
    faqs: List[FAQResponse]
    total: int
    query: str
    search_time_ms: float


class FAQFeedback(BaseModel):
    faq_id: int
    is_helpful: bool
    feedback_text: Optional[str] = None 