"""
Pydantic Schemas for Krishi Mitra API
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    phone: str
    location: Optional[str] = None
    preferred_language: Optional[str] = "en"


class UserResponse(BaseModel):
    id: int
    name: str
    phone: str
    location: Optional[str]
    preferred_language: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "en"
    session_id: Optional[int] = None
    user_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    session_id: int
    response: str
    suggestions: Optional[List[str]] = []
    language: str


# ─── Crop Record Schemas ───────────────────────────────────────────────────────

class CropRecordCreate(BaseModel):
    user_id: Optional[int] = None
    crop_name: str
    crop_name_local: Optional[str] = None
    area_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    season: Optional[str] = None
    sowing_date: Optional[str] = None
    current_stage: Optional[str] = None
    issues: Optional[str] = None
    notes: Optional[str] = None
    location: Optional[str] = None


class CropRecordResponse(CropRecordCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Weather Schemas ───────────────────────────────────────────────────────────

class WeatherRequest(BaseModel):
    location: str
    season: Optional[str] = None
    language: Optional[str] = "en"


class WeatherResponse(BaseModel):
    location: str
    advisory: str
    recommendations: Optional[List[str]] = []


# ─── Health Check ─────────────────────────────────────────────────────────────

class HealthCheckResponse(BaseModel):
    status: str
    message: str
