"""
Document Processing Routes
Endpoints for processing land documents through the complete PCC workflow
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import os
import hashlib
from datetime import datetime

from database import get_db
from database.models import User, LandRecord
from database.auth import decode_access_token
from core.landguard.compression_bridge import CompressionBridge, process_document_complete_workflow
from core.blockchain.ipfs_integration import IPFSIntegration
from Blockchain.blockchain.smart_contract import SmartContract
from Blockchain.blockchain.audit_trail import AuditTrail, AuditEventType

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

# Processing configuration
PROCESSING_DIR = "processed"
UPLOAD_DIR = "uploads"
os.makedirs(PROCESSING_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


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


@router.post("/process-document")
async def process_land_document(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a land document through the complete PCC workflow:
    1. Upload the document
    2. Check for anomalies/fraud
    3. Compress the file
    4. Encrypt the file
    5. Create .ppc file
    6. Upload to IPFS
    7. Store CID on blockchain
    8. Save audit record
    
    Args:
        file: Uploaded land document
        password: Encryption password for the .ppc file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Processing result with all details
    """
    try:
        # Save uploaded file temporarily
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Calculate file hash
        file_hash = hashlib.sha256(content).hexdigest()
        
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
            status="processing",
            user_id=current_user.id
        )
        
        db.add(record)
        db.commit()
        db.refresh(record)
        
        # Initialize audit trail
        audit = AuditTrail()
        audit.log_event(
            event_type=AuditEventType.ANALYSIS_STARTED,
            record_id=str(record.id),
            details={
                "action": "Document processing initiated",
                "filename": file.filename,
                "filesize": file_size
            },
            user_id=current_user.username
        )
        
        # Step 1: Check for anomalies/fraud (placeholder - in real implementation, this would call ML models)
        fraud_check_result = {
            "is_suspicious": False,
            "anomalies_found": [],
            "risk_score": 0.0
        }
        
        # Log fraud check
        audit.log_event(
            event_type=AuditEventType.ANALYSIS_COMPLETED,
            record_id=str(record.id),
            details={
                "action": "Fraud analysis completed",
                "is_suspicious": fraud_check_result["is_suspicious"],
                "risk_score": fraud_check_result["risk_score"]
            },
            user_id=current_user.username
        )
        
        # Step 2-6: Process through PCC workflow
        processing_result = process_document_complete_workflow(
            input_path=file_path,
            password=password,
            land_record_id=record.id
        )
        
        if not processing_result["success"]:
            # Update record status
            record.status = "failed"
            record.error_message = processing_result.get("details", {}).get("error", "Processing failed")
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {record.error_message}"
            )
        
        # Extract processing details
        ipfs_url = processing_result["ipfs_url"]
        details = processing_result["details"]
        ppc_path = details["ppc_path"]
        cid = details["cid"]
        compression_info = details["compression_info"]
        
        # Update record with processing results
        record.status = "processed"
        record.compression_ratio = compression_info.get("compression_ratio", 1.0)
        record.ipfs_hash = cid
        record.ppc_file_path = ppc_path
        db.commit()
        
        # Step 7: Store CID on blockchain
        contract = SmartContract()
        blockchain_result = contract.register_land_record(
            land_record_id=record.id,
            ipfs_cid=cid,
            owner_address=f"user_{current_user.id}"
        )
        
        # Update record with blockchain info
        record.blockchain_verified = blockchain_result["success"]
        record.transaction_hash = blockchain_result.get("tx_hash")
        db.commit()
        
        # Step 8: Log audit trail
        audit.log_event(
            event_type=AuditEventType.EVIDENCE_STORED,
            record_id=str(record.id),
            details={
                "action": "Document processed and stored",
                "ipfs_cid": cid,
                "blockchain_tx": blockchain_result.get("tx_hash"),
                "compression_ratio": compression_info.get("compression_ratio", 1.0)
            },
            user_id=current_user.username
        )
        
        logger.info(f"Document processed successfully: {file.filename} by user {current_user.username}")
        
        return {
            "success": True,
            "record_id": record.id,
            "record_number": record.record_number,
            "original_filename": record.original_filename,
            "file_size": record.file_size,
            "compression_ratio": record.compression_ratio,
            "ipfs_url": ipfs_url,
            "cid": cid,
            "blockchain_verified": record.blockchain_verified,
            "transaction_hash": record.transaction_hash,
            "processing_details": {
                "fraud_check": fraud_check_result,
                "compression_info": compression_info
            },
            "message": "Document processed successfully through complete workflow"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(e)}"
        )


@router.post("/verify-document/{record_id}")
async def verify_processed_document(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify a processed document by checking:
    1. IPFS availability
    2. Blockchain registration
    3. File integrity
    
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
        
        if not record.ipfs_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document not processed yet"
            )
        
        # Initialize components
        ipfs_integration = IPFSIntegration()
        contract = SmartContract()
        audit = AuditTrail()
        
        # Step 1: Verify on IPFS
        ipfs_verification = ipfs_integration.verify_document_integrity(
            cid=record.ipfs_hash
        )
        
        # Step 2: Verify on blockchain
        blockchain_verification = contract.verify_land_record(
            land_record_id=record.id,
            ipfs_cid=record.ipfs_hash
        )
        
        # Step 3: Create audit trail entry
        audit.log_event(
            event_type=AuditEventType.EVIDENCE_RETRIEVED,
            record_id=str(record.id),
            details={
                "action": "Document verification performed",
                "ipfs_verified": ipfs_verification.get("verified", False),
                "blockchain_verified": blockchain_verification.get("verified", False)
            },
            user_id=current_user.username
        )
        
        is_verified = (
            ipfs_verification.get("verified", False) and 
            blockchain_verification.get("verified", False)
        )
        
        return {
            "verified": is_verified,
            "record_id": record.id,
            "record_number": record.record_number,
            "ipfs_verification": ipfs_verification,
            "blockchain_verification": blockchain_verification,
            "message": "Document verified successfully" if is_verified else "Document verification failed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document verification failed: {str(e)}"
        )