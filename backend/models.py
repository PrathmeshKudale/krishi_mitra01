"""
SQLAlchemy ORM Models for Krishi Mitra
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, index=True)
    location = Column(String(200))
    state = Column(String(100), default="Maharashtra")
    preferred_language = Column(String(10), default="en")  # en, hi, mr
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("ChatSession", back_populates="user")
    crop_records = relationship("CropRecord", back_populates="user")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    language = Column(String(10), default="en")
    title = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class CropRecord(Base):
    __tablename__ = "crop_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    crop_name = Column(String(100), nullable=False)
    crop_name_local = Column(String(100))  # Hindi/Marathi name
    area_acres = Column(Float)
    soil_type = Column(String(100))
    irrigation_type = Column(String(100))
    season = Column(String(50))  # Kharif, Rabi, Zaid
    sowing_date = Column(String(50))
    expected_harvest = Column(String(50))
    current_stage = Column(String(100))  # sowing, germination, vegetative, flowering, harvest
    issues = Column(Text)
    notes = Column(Text)
    location = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="crop_records")


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(200), nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    rainfall_mm = Column(Float)
    wind_speed = Column(Float)
    condition = Column(String(100))
    advisory = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())


class DiseaseReport(Base):
    __tablename__ = "disease_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    crop_name = Column(String(100), nullable=False)
    symptoms = Column(Text, nullable=False)
    diagnosis = Column(Text)
    treatment = Column(Text)
    image_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(Integer, primary_key=True, index=True)
    crop_name = Column(String(100), nullable=False)
    market_name = Column(String(200))
    state = Column(String(100))
    min_price = Column(Float)
    max_price = Column(Float)
    modal_price = Column(Float)
    unit = Column(String(20), default="quintal")
    date = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
