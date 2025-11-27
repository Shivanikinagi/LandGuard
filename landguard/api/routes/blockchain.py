"""
Blockchain Routes
Blockchain verification and IPFS storage endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from database import get_db
from database.models import User, LandRecord
from database.auth import decode_access_token

router = APIRouter()
security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """Get current user from token (optional)"""
    if not credentials:
        return None
    
    try:
        payload = decode_access_token(credentials.credentials)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        return user
    except Exception:
        return None


def get_current_user_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from token (required)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.get("/status")
async def get_blockchain_status() -> Dict[str, Any]:
    """
    Get blockchain service status (no authentication required)
    
    Returns:
        Blockchain status information
    """
    return {
        "available": False,
        "message": "Blockchain services not configured",
        "ipfs_available": False,
        "ethereum_available": False,
        "network": None
    }


@router.post("/verify/{record_id}")
async def verify_on_blockchain(
    record_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify a land record on blockchain
    
    Args:
        record_id: Land record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Verification result
    """
    try:
        # Get record
        record = db.query(LandRecord).filter(
            LandRecord.id == record_id,
            LandRecord.user_id == current_user.id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found"
            )
        
        # Blockchain services not configured - return message
        return {
            "success": False,
            "message": "Blockchain services not configured",
            "record_id": record_id,
            "verified": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying on blockchain: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@router.get("/status/{record_id}")
async def get_verification_status(
    record_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get blockchain verification status for a record
    
    Args:
        record_id: Land record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Verification status
    """
    try:
        # Get record
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
            "record_id": record_id,
            "verified": record.blockchain_verified or False,
            "ipfs_hash": record.ipfs_hash,
            "transaction_hash": record.transaction_hash,
            "message": "Blockchain verification status"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting verification status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}"
        )


@router.post("/ipfs/upload/{record_id}")
async def upload_to_ipfs(
    record_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload record to IPFS
    
    Args:
        record_id: Land record ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        IPFS upload result
    """
    try:
        # Get record
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
            "success": False,
            "message": "IPFS services not configured",
            "record_id": record_id,
            "ipfs_hash": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading to IPFS: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"IPFS upload failed: {str(e)}"
        )


@router.get("/ipfs/retrieve/{ipfs_hash}")
async def retrieve_from_ipfs(
    ipfs_hash: str,
    current_user: User = Depends(get_current_user_optional)
) -> Dict[str, Any]:
    """
    Retrieve record from IPFS
    
    Args:
        ipfs_hash: IPFS hash
        current_user: Current user (optional)
        
    Returns:
        Retrieved data
    """
    return {
        "success": False,
        "message": "IPFS services not configured",
        "ipfs_hash": ipfs_hash,
        "data": None
    }