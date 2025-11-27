"""
Upload Routes
File upload and management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import logging
import os
import hashlib
from datetime import datetime

from database import get_db
from database.models import User, LandRecord
from database.auth import decode_access_token

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Upload configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".doc", ".docx"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/records")
async def get_upload_records(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's upload records
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of upload records
    """
    try:
        records = db.query(LandRecord).filter(
            LandRecord.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        return [
            {
                "id": record.id,
                "record_number": record.record_number,
                "owner_name": record.owner_name,
                "location": record.location,
                "status": record.status,
                "original_filename": record.original_filename,
                "file_size": record.file_size,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
            for record in records
        ]
        
    except Exception as e:
        logger.error(f"Error getting upload records: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get records: {str(e)}"
        )


@router.get("/record/{record_id}")
async def get_record_details(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific record
    
    Args:
        record_id: Record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Record details
    """
    try:
        record = db.query(LandRecord).filter(
            LandRecord.id == record_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        return {
            "id": record.id,
            "record_number": record.record_number,
            "owner_name": record.owner_name,
            "location": record.location,
            "area": record.area,
            "document_type": record.document_type,
            "status": record.status,
            "original_filename": record.original_filename,
            "file_size": record.file_size,
            "file_hash": record.file_hash,
            "compression_ratio": record.compression_ratio,
            "ipfs_hash": record.ipfs_hash,
            "blockchain_verified": record.blockchain_verified,
            "transaction_hash": record.transaction_hash,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting record details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get record: {str(e)}"
        )


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a land document
    
    Args:
        file: Uploaded file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created record details
    """
    try:
        # Validate file
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create database record
        record = LandRecord(
            record_number=f"REC-{timestamp}-{current_user.id}",
            original_filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            status="uploaded",
            user_id=current_user.id
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        logger.info(f"File uploaded successfully: {file.filename} by user {current_user.username}")
        
        return {
            "id": record.id,
            "record_number": record.record_number,
            "status": record.status,
            "original_filename": record.original_filename,
            "file_size": record.file_size,
            "file_hash": record.file_hash,
            "message": "File uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete("/record/{record_id}")
async def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a record
    
    Args:
        record_id: Record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    try:
        record = db.query(LandRecord).filter(
            LandRecord.id == record_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        # Delete file if exists
        if os.path.exists(record.file_path):
            os.remove(record.file_path)
        
        # Delete database record
        db.delete(record)
        db.commit()
        
        logger.info(f"Record deleted: {record_id} by user {current_user.username}")
        
        return {
            "message": "Record deleted successfully",
            "record_id": record_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting record: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )