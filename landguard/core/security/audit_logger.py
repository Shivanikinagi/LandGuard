"""
Security audit logging for LandGuard.
Tracks security events, access attempts, and anomalies.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum


class SecurityEventType(Enum):
    """Types of security events."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_FAILURE = "authz_failure"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    FILE_UPLOAD = "file_upload"
    FILE_UPLOAD_REJECTED = "file_upload_rejected"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SECURITY_SCAN = "security_scan"
    CONFIG_CHANGE = "config_change"


class SecurityEvent:
    """Represents a security event."""
    
    def __init__(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        severity: str = "info"
    ):
        """
        Initialize security event.
        
        Args:
            event_type: Type of security event
            user_id: User identifier
            ip_address: Client IP address
            resource: Resource being accessed/modified
            action: Action being performed
            success: Whether the action was successful
            details: Additional event details
            severity: Event severity (info, warning, error, critical)
        """
        self.event_type = event_type
        self.user_id = user_id
        self.ip_address = ip_address
        self.resource = resource
        self.action = action
        self.success = success
        self.details = details or {}
        self.severity = severity
        self.timestamp = datetime.utcnow()
        self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'resource': self.resource,
            'action': self.action,
            'success': self.success,
            'severity': self.severity,
            'details': self.details
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AuditLogger:
    """Security audit logger."""
    
    def __init__(
        self,
        log_file: Optional[Path] = None,
        log_to_console: bool = True,
        log_level: str = "INFO"
    ):
        """
        Initialize audit logger.
        
        Args:
            log_file: Path to audit log file
            log_to_console: Whether to log to console
            log_level: Logging level
        """
        self.log_file = log_file
        self.log_to_console = log_to_console
        
        # Set up Python logger
        self.logger = logging.getLogger('landguard.security.audit')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Add file handler if log file specified
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(file_handler)
        
        # Add console handler if requested
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            self.logger.addHandler(console_handler)
        
        # Event storage for in-memory analysis
        self.events: List[SecurityEvent] = []
        self.max_events_in_memory = 1000
    
    def log_event(self, event: SecurityEvent):
        """
        Log a security event.
        
        Args:
            event: SecurityEvent to log
        """
        # Add to in-memory storage
        self.events.append(event)
        
        # Trim if exceeds max
        if len(self.events) > self.max_events_in_memory:
            self.events = self.events[-self.max_events_in_memory:]
        
        # Log to file/console
        log_message = (
            f"[{event.event_type.value}] "
            f"User: {event.user_id or 'unknown'} "
            f"IP: {event.ip_address or 'unknown'} "
            f"Resource: {event.resource or 'N/A'} "
            f"Action: {event.action or 'N/A'} "
            f"Success: {event.success} "
            f"Details: {json.dumps(event.details)}"
        )
        
        # Log at appropriate level based on severity
        if event.severity == "critical":
            self.logger.critical(log_message)
        elif event.severity == "error":
            self.logger.error(log_message)
        elif event.severity == "warning":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
    
    def log_authentication(
        self,
        user_id: str,
        ip_address: str,
        success: bool,
        auth_method: str = "api_key",
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authentication attempt."""
        event = SecurityEvent(
            event_type=SecurityEventType.LOGIN_SUCCESS if success else SecurityEventType.LOGIN_FAILURE,
            user_id=user_id,
            ip_address=ip_address,
            action=f"authenticate_{auth_method}",
            success=success,
            details=details or {},
            severity="info" if success else "warning"
        )
        self.log_event(event)
    
    def log_authorization_failure(
        self,
        user_id: str,
        ip_address: str,
        resource: str,
        required_permission: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authorization failure."""
        event = SecurityEvent(
            event_type=SecurityEventType.AUTHORIZATION_FAILURE,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=f"access_denied_{required_permission}",
            success=False,
            details=details or {},
            severity="warning"
        )
        self.log_event(event)
    
    def log_rate_limit_exceeded(
        self,
        identifier: str,
        ip_address: str,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log rate limit exceeded."""
        event = SecurityEvent(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            user_id=identifier,
            ip_address=ip_address,
            resource=endpoint,
            action="rate_limit_check",
            success=False,
            details=details or {},
            severity="warning"
        )
        self.log_event(event)
    
    def log_file_upload(
        self,
        user_id: str,
        ip_address: str,
        filename: str,
        file_size: int,
        success: bool,
        rejection_reason: Optional[str] = None
    ):
        """Log file upload attempt."""
        event = SecurityEvent(
            event_type=SecurityEventType.FILE_UPLOAD if success else SecurityEventType.FILE_UPLOAD_REJECTED,
            user_id=user_id,
            ip_address=ip_address,
            resource=filename,
            action="upload_file",
            success=success,
            details={
                'filename': filename,
                'file_size': file_size,
                'rejection_reason': rejection_reason
            },
            severity="info" if success else "warning"
        )
        self.log_event(event)
    
    def log_data_access(
        self,
        user_id: str,
        ip_address: str,
        resource: str,
        action: str = "read",
        details: Optional[Dict[str, Any]] = None
    ):
        """Log data access."""
        event = SecurityEvent(
            event_type=SecurityEventType.DATA_ACCESS,
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            success=True,
            details=details or {},
            severity="info"
        )
        self.log_event(event)
    
    def log_suspicious_activity(
        self,
        user_id: Optional[str],
        ip_address: str,
        activity_type: str,
        details: Dict[str, Any]
    ):
        """Log suspicious activity."""
        event = SecurityEvent(
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_id=user_id,
            ip_address=ip_address,
            action=activity_type,
            success=False,
            details=details,
            severity="error"
        )
        self.log_event(event)
    
    def get_recent_events(
        self,
        count: int = 100,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> List[SecurityEvent]:
        """
        Get recent security events with optional filtering.
        
        Args:
            count: Maximum number of events to return
            event_type: Filter by event type
            user_id: Filter by user ID
            ip_address: Filter by IP address
            
        Returns:
            List of matching events
        """
        filtered_events = self.events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if ip_address:
            filtered_events = [e for e in filtered_events if e.ip_address == ip_address]
        
        return filtered_events[-count:]
    
    def get_failed_authentication_attempts(
        self,
        time_window_minutes: int = 60
    ) -> List[SecurityEvent]:
        """Get failed authentication attempts in time window."""
        cutoff = datetime.utcnow().timestamp() - (time_window_minutes * 60)
        
        return [
            event for event in self.events
            if event.event_type == SecurityEventType.LOGIN_FAILURE
            and event.timestamp.timestamp() > cutoff
        ]
    
    def export_logs(self, output_file: Path, format: str = "json"):
        """
        Export audit logs to file.
        
        Args:
            output_file: Output file path
            format: Output format (json or csv)
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump([event.to_dict() for event in self.events], f, indent=2)
        
        elif format == "csv":
            import csv
            
            with open(output_file, 'w', newline='') as f:
                if self.events:
                    fieldnames = self.events[0].to_dict().keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for event in self.events:
                        row = event.to_dict()
                        # Convert dict fields to JSON strings
                        row['details'] = json.dumps(row['details'])
                        writer.writerow(row)