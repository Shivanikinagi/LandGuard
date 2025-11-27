"""
Database Repositories
Data access layer for database operations
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.models import User, LandRecord, AnalysisResult, AuditLog


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
    def get_by_api_key(db: Session, api_key: str) -> Optional[User]:
        """Get user by API key"""
        return db.query(User).filter(User.api_key == api_key).first()
    
    @staticmethod
    def create(db: Session, user: User) -> User:
        """Create a new user"""
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update(db: Session, user: User) -> User:
        """Update user"""
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete(db: Session, user: User) -> None:
        """Delete user"""
        db.delete(user)
        db.commit()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()


class LandRecordRepository:
    """Repository for LandRecord operations"""
    
    @staticmethod
    def get_by_id(db: Session, record_id: int) -> Optional[LandRecord]:
        """Get land record by ID"""
        return db.query(LandRecord).filter(LandRecord.id == record_id).first()
    
    @staticmethod
    def get_by_record_number(db: Session, record_number: str) -> Optional[LandRecord]:
        """Get land record by record number"""
        return db.query(LandRecord).filter(LandRecord.record_number == record_number).first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[LandRecord]:
        """Get land records by user ID"""
        return db.query(LandRecord).filter(
            LandRecord.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> List[LandRecord]:
        """Get land records by status"""
        return db.query(LandRecord).filter(
            LandRecord.status == status
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, record: LandRecord) -> LandRecord:
        """Create a new land record"""
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def update(db: Session, record: LandRecord) -> LandRecord:
        """Update land record"""
        db.commit()
        db.refresh(record)
        return record
    
    @staticmethod
    def delete(db: Session, record: LandRecord) -> None:
        """Delete land record"""
        db.delete(record)
        db.commit()
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[LandRecord]:
        """Get all land records with pagination"""
        return db.query(LandRecord).offset(skip).limit(limit).all()
    
    @staticmethod
    def search(db: Session, query: str, skip: int = 0, limit: int = 100) -> List[LandRecord]:
        """Search land records"""
        search_filter = or_(
            LandRecord.record_number.ilike(f"%{query}%"),
            LandRecord.owner_name.ilike(f"%{query}%"),
            LandRecord.location.ilike(f"%{query}%")
        )
        return db.query(LandRecord).filter(search_filter).offset(skip).limit(limit).all()


class AnalysisResultRepository:
    """Repository for AnalysisResult operations"""
    
    @staticmethod
    def get_by_id(db: Session, analysis_id: int) -> Optional[AnalysisResult]:
        """Get analysis result by ID"""
        return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    
    @staticmethod
    def get_by_land_record(db: Session, land_record_id: int) -> List[AnalysisResult]:
        """Get analysis results for a land record"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.land_record_id == land_record_id
        ).all()
    
    @staticmethod
    def get_fraud_detected(db: Session, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results with fraud detected"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.fraud_detected == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_anomalies_detected(db: Session, skip: int = 0, limit: int = 100) -> List[AnalysisResult]:
        """Get analysis results with anomalies detected"""
        return db.query(AnalysisResult).filter(
            AnalysisResult.anomaly_detected == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def create(db: Session, analysis: AnalysisResult) -> AnalysisResult:
        """Create a new analysis result"""
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def update(db: Session, analysis: AnalysisResult) -> AnalysisResult:
        """Update analysis result"""
        db.commit()
        db.refresh(analysis)
        return analysis
    
    @staticmethod
    def delete(db: Session, analysis: AnalysisResult) -> None:
        """Delete analysis result"""
        db.delete(analysis)
        db.commit()


class AuditLogRepository:
    """Repository for AuditLog operations"""
    
    @staticmethod
    def create(db: Session, log: AuditLog) -> AuditLog:
        """Create a new audit log entry"""
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    
    @staticmethod
    def get_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a user"""
        return db.query(AuditLog).filter(
            AuditLog.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_entity(db: Session, entity_type: str, entity_id: int) -> List[AuditLog]:
        """Get audit logs for an entity"""
        return db.query(AuditLog).filter(
            and_(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id
            )
        ).all()
    
    @staticmethod
    def get_recent(db: Session, limit: int = 100) -> List[AuditLog]:
        """Get recent audit logs"""
        return db.query(AuditLog).order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()