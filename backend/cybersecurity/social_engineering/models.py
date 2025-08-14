"""
Social Engineering Module - Models
Modèles de données pour les campagnes de social engineering et phishing
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CampaignType(str, Enum):
    PHISHING_EMAIL = "phishing_email"
    SPEAR_PHISHING = "spear_phishing"
    SMS_PHISHING = "sms_phishing"
    VOICE_PHISHING = "voice_phishing"
    SOCIAL_MEDIA = "social_media"
    PHYSICAL_APPROACH = "physical_approach"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SocialEngineeringCampaignRequest(BaseModel):
    campaign_name: str
    campaign_type: CampaignType
    description: Optional[str] = None
    target_groups: List[str]  # Liste des groupes cibles
    template_id: Optional[str] = None
    schedule_date: Optional[str] = None
    training_mode: bool = True  # Mode formation ou réel
    settings: Optional[Dict[str, Any]] = None

class Target(BaseModel):
    target_id: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    group: str
    metadata: Optional[Dict[str, Any]] = None

class PhishingTemplate(BaseModel):
    template_id: str
    name: str
    type: CampaignType
    subject: Optional[str] = None
    content: str
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    landing_page_url: Optional[str] = None
    difficulty_level: str  # easy, medium, hard
    industry_focus: Optional[str] = None
    language: str = "fr"
    created_at: str
    updated_at: str

class CampaignInteraction(BaseModel):
    interaction_id: str
    campaign_id: str
    target_id: str
    interaction_type: str  # email_sent, email_opened, link_clicked, data_submitted, reported
    timestamp: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    submitted_data: Optional[Dict[str, Any]] = None

class CampaignResult(BaseModel):
    campaign_id: str
    campaign_name: str
    campaign_type: CampaignType
    status: CampaignStatus
    created_at: str
    completed_at: Optional[str] = None
    total_targets: int
    emails_sent: int = 0
    emails_opened: int = 0
    links_clicked: int = 0
    data_submitted: int = 0
    reported_as_phishing: int = 0
    success_rate: float = 0.0
    click_rate: float = 0.0
    report_rate: float = 0.0
    interactions: List[CampaignInteraction] = []

class SecurityAwareness(BaseModel):
    target_id: str
    total_campaigns: int
    successful_identifications: int
    failed_identifications: int
    improvement_score: float
    last_training_date: Optional[str] = None
    risk_level: str  # low, medium, high
    recommendations: List[str] = []

class SocialEngineeringReport(BaseModel):
    report_id: str
    campaign_id: str
    generated_at: str
    summary: Dict[str, Any]
    detailed_results: CampaignResult
    target_analysis: List[SecurityAwareness]
    recommendations: List[str]
    training_suggestions: List[str]