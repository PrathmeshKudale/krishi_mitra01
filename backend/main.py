"""
Krishi Mitra - FastAPI Backend
AI Farming Assistant for Indian Farmers
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import uvicorn

from database import engine, get_db, Base
from models import User, ChatSession, ChatMessage, CropRecord, WeatherLog
from schemas import (
    UserCreate, UserResponse,
    ChatRequest, ChatResponse,
    CropRecordCreate, CropRecordResponse,
    WeatherRequest, WeatherResponse,
    HealthCheckResponse
)
from ai_service import KrishiAIService

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Krishi Mitra API",
    description="AI Farming Assistant for Indian Farmers",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = KrishiAIService()


# ─── Health Check ────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthCheckResponse)
def health_check():
    return {"status": "ok", "message": "Krishi Mitra API is running 🌱"}


# ─── User Routes ─────────────────────────────────────────────────────────────

@app.post("/api/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == user.phone).first()
    if existing:
        return existing
    db_user = User(
        name=user.name,
        phone=user.phone,
        location=user.location,
        preferred_language=user.preferred_language
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ─── Chat Routes ─────────────────────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Main AI chat endpoint for farming advice."""
    # Get or create session
    session = None
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == request.session_id
        ).first()

    if not session:
        session = ChatSession(
            user_id=request.user_id,
            language=request.language or "en"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Fetch history for context
    history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()

    history_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history)
    ]

    # Get AI response
    response_text, suggestions = ai_service.get_farming_advice(
        message=request.message,
        language=request.language or "en",
        context=request.context or {},
        history=history_messages
    )

    # Save messages to DB
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message
    )
    ai_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text
    )
    db.add_all([user_msg, ai_msg])
    db.commit()

    return ChatResponse(
        session_id=session.id,
        response=response_text,
        suggestions=suggestions,
        language=request.language or "en"
    )


@app.get("/api/chat/sessions/{user_id}")
def get_user_sessions(user_id: int, db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user_id
    ).order_by(ChatSession.created_at.desc()).limit(20).all()
    return sessions


@app.get("/api/chat/history/{session_id}")
def get_chat_history(session_id: int, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages


# ─── Crop Records ─────────────────────────────────────────────────────────────

@app.post("/api/crops", response_model=CropRecordResponse)
def create_crop_record(record: CropRecordCreate, db: Session = Depends(get_db)):
    db_record = CropRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


@app.get("/api/crops/{user_id}")
def get_crop_records(user_id: int, db: Session = Depends(get_db)):
    records = db.query(CropRecord).filter(
        CropRecord.user_id == user_id
    ).order_by(CropRecord.created_at.desc()).all()
    return records


@app.get("/api/crops/{user_id}/{record_id}/advice")
def get_crop_advice(user_id: int, record_id: int, db: Session = Depends(get_db)):
    record = db.query(CropRecord).filter(CropRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Crop record not found")
    advice, _ = ai_service.get_crop_specific_advice(record)
    return {"advice": advice, "crop": record.crop_name}


# ─── Disease Detection ────────────────────────────────────────────────────────

@app.post("/api/disease/analyze")
def analyze_disease(
    crop_name: str,
    symptoms: str,
    language: str = "en",
    db: Session = Depends(get_db)
):
    analysis = ai_service.analyze_disease(crop_name, symptoms, language)
    return analysis


# ─── Market Prices ─────────────────────────────────────────────────────────────

@app.get("/api/market/prices")
def get_market_prices(
    crop: Optional[str] = None,
    state: Optional[str] = "Maharashtra",
    language: str = "en"
):
    prices = ai_service.get_market_insights(crop, state, language)
    return prices


# ─── Weather Advisory ─────────────────────────────────────────────────────────

@app.post("/api/weather/advisory")
def get_weather_advisory(request: WeatherRequest):
    advisory = ai_service.get_weather_advisory(
        location=request.location,
        season=request.season,
        language=request.language
    )
    return {"advisory": advisory}


# ─── Scheme Finder ────────────────────────────────────────────────────────────

@app.get("/api/schemes")
def get_schemes(
    state: str = "Maharashtra",
    crop: Optional[str] = None,
    language: str = "en"
):
    schemes = ai_service.get_government_schemes(state, crop, language)
    return {"schemes": schemes}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
