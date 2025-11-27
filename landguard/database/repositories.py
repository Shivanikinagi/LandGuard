"""
Database Repositories
Data access layer for models
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.models import User, LandRecord, Analysis, AuditLog


class UserRepository:
    """Repository for User operations"""
    
    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, user: User) -> User:
        """Create new user"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


class LandRecordRepository:
    """Repository for LandRecord operations"""
    
    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[LandRecord]:
        """Get land record by ID"""
        return db.query(LandRecord).filter(LandRecord.id == record_id).first()
    
    @staticmethod
    def get_by_record_number(db: Session, record_number: str) -> Optional[LandRecord]:
        """Get land record by record number"""
        return db.query(LandRecord).filter(
            LandRecord.record_number == record_number
        ).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[LandRecord]:
        """Get all land records with pagination"""
        query = db.query(LandRecord)
        
        if status:
            query = query.filter(LandRecord.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, land_record: LandRecord) -> LandRecord:
        """Create new land record"""
        db.add(land_record)
        db.commit()
        db.refresh(land_record)
        return land_record
    
    @staticmethod
    def update(db: Session, land_record: LandRecord) -> LandRecord:
        """Update land record"""
        db.commit()
        db.refresh(land_record)
        return land_record


class AnalysisRepository:
    """Repository for Analysis operations"""
    
    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID"""
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    @staticmethod
    def get_by_land_record(
        db: Session,
        land_record_id: int
    ) -> List[Analysis]:
        """Get all analyses for a land record"""
        return db.query(Analysis).filter(
            Analysis.land_record_id == land_record_id
        ).all()
    
    @staticmethod
    def create(db: Session, analysis: Analysis) -> Analysis:
        """Create new analysis"""
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis