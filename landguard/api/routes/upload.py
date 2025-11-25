"""
File upload endpoints.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status

from api.models.responses import UploadResponse, ErrorResponse
from api.dependencies import get_analyst_user, check_rate_limit, audit_logger
from core.security.validator import FileValidator, FileType
from core.security.sanitizer import DataSanitizer

router = APIRouter(prefix="/api/v1", tags=["upload"])

# Upload directory
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}},
    dependencies=[Depends(check_rate_limit)]
)
async def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_analyst_user)
):
    """
    Upload a JSON or CSV file for analysis.
    
    Requires analyst or admin role.
    Maximum file size: 100 MB.
    """
    try:
        # Validate filename
        is_valid, error = FileValidator.validate_filename(file.filename)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Sanitize filename
        safe_filename = DataSanitizer.sanitize_filename(file.filename)
        
        # Determine file type
        file_ext = Path(safe_filename).suffix.lower()
        if file_ext == '.json':
            file_type = FileType.JSON
        elif file_ext == '.csv':
            file_type = FileType.CSV
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JSON and CSV files are supported"
            )
        
        # Validate file extension
        is_valid, error = FileValidator.validate_file_extension(safe_filename, file_type)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        is_valid, error = FileValidator.validate_file_size(file_size)
        if not is_valid:
            # Log rejected upload
            audit_logger.log_file_upload(
                user_id=user.get('user_id', 'unknown'),
                ip_address="unknown",
                filename=safe_filename,
                file_size=file_size,
                success=False,
                rejection_reason=error
            )
            
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=error
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save file with unique name
        unique_filename = f"{file_id}_{safe_filename}"
        file_path = UPLOAD_DIR / unique_filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Validate file content
        is_valid, error = FileValidator.validate_file_content(file_path, file_type)
        if not is_valid:
            # Delete invalid file
            file_path.unlink()
            
            # Log rejected upload
            audit_logger.log_file_upload(
                user_id=user.get('user_id', 'unknown'),
                ip_address="unknown",
                filename=safe_filename,
                file_size=file_size,
                success=False,
                rejection_reason=error
            )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        
        # Parse and validate JSON content
        if file_type == FileType.JSON:
            try:
                data = json.loads(content)
                # Basic validation that it's a list or dict
                if not isinstance(data, (list, dict)):
                    raise ValueError("Invalid JSON structure")
            except json.JSONDecodeError as e:
                file_path.unlink()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid JSON: {str(e)}"
                )
        
        # Log successful upload
        audit_logger.log_file_upload(
            user_id=user.get('user_id', 'unknown'),
            ip_address="unknown",
            filename=safe_filename,
            file_size=file_size,
            success=True,
            rejection_reason=None
        )
        
        return UploadResponse(
            file_id=file_id,
            filename=safe_filename,
            size_bytes=file_size,
            status="uploaded",
            message="File uploaded successfully",
            analysis_job_id=None  # TODO: Implement async analysis job
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/uploads/{file_id}", response_model=UploadResponse)
async def get_upload_status(
    file_id: str,
    user: dict = Depends(get_analyst_user)
):
    """
    Get upload status by file ID.
    
    Note: This is a placeholder. In production, track upload status in database.
    """
    # TODO: Implement upload status tracking
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Upload status tracking not yet implemented"
    )