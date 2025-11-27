"""
Database Models
SQLAlchemy ORM models for the database
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Changed to match DB
    full_name = Column(String(200), nullable=True)
    role = Column(String(50), nullable=False, default="user")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    land_records = relationship("LandRecord", back_populates="user", cascade="all, delete-orphan")


class LandRecord(Base):
    """Land record model"""
    __tablename__ = "land_records"
    
    id = Column(Integer, primary_key=True, index=True)
    record_number = Column(String(50), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=True)  # Made nullable
    location = Column(String(255), nullable=True)    # Made nullable
    area = Column(Float, nullable=True)              # Made nullable
    document_type = Column(String(50), nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=True)
    
    # Processing information
    compressed_file_path = Column(String(500), nullable=True)
    encrypted_file_path = Column(String(500), nullable=True)
    ppc_file_path = Column(String(500), nullable=True)
    compression_ratio = Column(Float, nullable=True)
    
    # Blockchain information
    ipfs_hash = Column(String(100), nullable=True)
    blockchain_verified = Column(Boolean, default=False)
    transaction_hash = Column(String(100), nullable=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="land_records")
    analyses = relationship("AnalysisResult", back_populates="land_record", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalysisResult(Base):
    """Analysis result model"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    land_record_id = Column(Integer, ForeignKey("land_records.id"), nullable=False)
    
    # Fraud detection
    fraud_detected = Column(Boolean, default=False, nullable=False)
    fraud_score = Column(Float, default=0.0, nullable=False)
    fraud_indicators = Column(JSON, nullable=True)
    
    # Anomaly detection
    anomaly_detected = Column(Boolean, default=False, nullable=False)
    anomaly_score = Column(Float, default=0.0, nullable=False)
    anomaly_types = Column(JSON, nullable=True)
    
    # Analysis details
    text_analysis = Column(JSON, nullable=True)
    pattern_analysis = Column(JSON, nullable=True)
    risk_assessment = Column(String(20), nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Metadata
    analyzed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    model_version = Column(String(20), nullable=True)
    
    # Relationships
    land_record = relationship("LandRecord", back_populates="analyses")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)