"""
Database Models
SQLAlchemy ORM Models for PostgreSQL
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database.connection import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="VIEWER")  # ADMIN, ANALYST, VIEWER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class LandRecord(Base):
    """Land Record model"""
    __tablename__ = "land_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_number = Column(String(100), unique=True, nullable=False, index=True)
    owner_name = Column(String(200), nullable=False)
    location = Column(String(500), nullable=False)
    area = Column(Float, nullable=False)
    status = Column(String(50), default="PENDING")  # PENDING, ANALYZED, VERIFIED, FLAGGED
    document_path = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyses = relationship("Analysis", back_populates="land_record", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LandRecord(id={self.id}, record_number='{self.record_number}', status='{self.status}')>"


class Analysis(Base):
    """Analysis Result model"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id", ondelete="CASCADE"), nullable=False)
    risk_level = Column(String(50), nullable=False)  # LOW, MEDIUM, HIGH
    fraud_probability = Column(Float, nullable=False)
    flags = Column(JSON, default=[])  # List of detected issues
    recommendation = Column(Text)
    analyzed_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    land_record = relationship("LandRecord", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, land_record_id={self.land_record_id}, risk_level='{self.risk_level}')>"


class AuditLog(Base):
    """Audit Log model for tracking system activities"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"