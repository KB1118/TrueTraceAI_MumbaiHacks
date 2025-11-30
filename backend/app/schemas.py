"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Auth Schemas
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Crisis Schemas
class CrisisCreate(BaseModel):
    title: str
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class CrisisResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    keywords: Optional[List[str]]
    detected_at: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = Field(None, alias="crisis_metadata")
    
    class Config:
        from_attributes = True
        populate_by_name = True


# Cluster Schemas
class RumorClusterResponse(BaseModel):
    id: int
    crisis_id: int
    topic_label: Optional[str]
    post_ids: Optional[List[str]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Claim Schemas
class ClaimResponse(BaseModel):
    id: int
    cluster_id: int
    text: str
    verdict: Optional[str]
    confidence_score: Optional[float]
    volatility_score: Optional[float]
    reasoning: Optional[str]
    evidence_citations: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ClaimWithCards(ClaimResponse):
    cards: List[Dict[str, Any]] = []


# Verification Schemas
class VerifyRequest(BaseModel):
    text: str


class VerifyResponse(BaseModel):
    claim: str
    verdict: str
    confidence_score: float
    volatility_score: float
    reasoning: str
    evidence_citations: List[str]
    card: Dict[str, Any]


class MultimodalSourceMetadata(BaseModel):
    rendered_content: Optional[str] = None
    references: Optional[List[Dict[str, Any]]] = None


class MultimodalFileMetadata(BaseModel):
    name: Optional[str]
    display_name: Optional[str]
    mime_type: Optional[str]
    state: Optional[str]
    size_bytes: Optional[int]


class MultimodalFactCheckResponse(BaseModel):
    model: str
    analysis_text: str
    verdict_summary: Optional[str] = None
    sources: Optional[MultimodalSourceMetadata] = None
    file: Optional[MultimodalFileMetadata] = None
    latency_ms: Optional[int] = None
    used_google_search: bool = True


# Pipeline Schemas
class PipelineTrigger(BaseModel):
    force: bool = False


class PipelineStatus(BaseModel):
    status: str
    message: str
    last_run: Optional[datetime] = None

