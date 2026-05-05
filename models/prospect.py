from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    ENGLISH = "english"
    HINDI = "hindi"
    MARATHI = "marathi"

class FormalityLevel(str, Enum):
    FORMAL = "formal"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    CONVERSATIONAL = "conversational"

class LanguageType(str, Enum):
    TECHNICAL = "technical"
    BUSINESS = "business"
    CREATIVE = "creative"
    ACADEMIC = "academic"

class ToneType(str, Enum):
    FRIENDLY = "friendly"
    DIRECT = "direct"
    ENTHUSIASTIC = "enthusiastic"
    CONSERVATIVE = "conservative"

class CommunicationStyle(BaseModel):
    formality_level: FormalityLevel
    language_type: LanguageType
    tone_preference: ToneType
    confidence_score: float
    analysis_summary: str

class ActivityItem(BaseModel):
    type: str  # "post", "job_change", "article_share", etc.
    content: str
    date: str
    engagement: Optional[int] = None

class ProspectProfile(BaseModel):
    id: str
    name: str
    company: str
    role: str
    industry: str
    location: str
    linkedin_url: str
    interests: List[str]
    recent_activity: List[ActivityItem]
    communication_style: CommunicationStyle
    about_section: str
    created_at: datetime

class ChannelMessage(BaseModel):
    channel: str
    subject: Optional[str] = None
    content: str
    word_count: int
    personalization_elements: List[str]
    success_score: Optional[int] = None
    response_probability: Optional[str] = None
    prob_color: Optional[str] = None
    scoring_factors: Optional[List[str]] = None
    optimization_suggestions: Optional[List[str]] = None
    language: Optional[Language] = Language.ENGLISH

class ChannelMessages(BaseModel):
    prospect_id: str
    email: ChannelMessage
    linkedin_dm: ChannelMessage
    whatsapp: ChannelMessage
    sms: ChannelMessage
    instagram_dm: ChannelMessage
    generated_at: datetime
    generation_time_seconds: float