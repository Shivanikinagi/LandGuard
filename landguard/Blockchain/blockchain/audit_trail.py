"""
LandGuard Immutable Audit Trail
Tamper-proof logging of all fraud analysis activities
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum
import uuid


class AuditEventType(Enum):
    """Types of audit events"""
    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"
    FRAUD_DETECTED = "fraud_detected"
    EVIDENCE_STORED = "evidence_stored"
    EVIDENCE_RETRIEVED = "evidence_retrieved"
    REPORT_GENERATED = "report_generated"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    ERROR_OCCURRED = "error_occurred"


class AuditTrail:
    """
    Immutable audit trail for fraud detection activities
    Each entry is cryptographically linked to previous entries
    """
    
    def __init__(self, storage_dir: str = 'blockchain/storage/audit_logs'):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_log_file = self.storage_dir / 'audit_trail.jsonl'
        self.index_file = self.storage_dir / 'audit_index.json'
        
        # Initialize if needed
        self._initialize()
    
    def _initialize(self):
        """Initialize audit trail"""
        if not self.index_file.exists():
            index = {
                'created_at': datetime.utcnow().isoformat(),
                'total_entries': 0,
                'last_hash': None,
                'version': '1.0'
            }
            self._save_index(index)
    
    def _load_index(self) -> Dict:
        """Load audit trail index"""
        with open(self.index_file, 'r') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Save audit trail index"""
        with open(self.index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def log_event(self, 
                  event_type: AuditEventType,
                  record_id: str,
                  details: Dict,
                  user_id: str = 'system',
                  session_id: str = None) -> str:
        """
        Log an audit event
        
        Args:
            event_type: Type of event
            record_id: Related record ID
            details: Event details
            user_id: User who triggered the event
            session_id: Session identifier
        
        Returns:
            Event ID
        """
        from hash_manager import HashManager
        
        # Load current index
        index = self._load_index()
        
        # Create event entry
        event_id = str(uuid.uuid4())
        event = {
            'event_id': event_id,
            'event_type': event_type.value,
            'record_id': record_id,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'session_id': session_id or str(uuid.uuid4()),
            'details': details,
            'sequence_number': index['total_entries'] + 1,
            'previous_hash': index['last_hash']
        }
        
        # Calculate hash for this event
        hash_mgr = HashManager()
        event_hash = hash_mgr.hash_data(event)
        event['event_hash'] = event_hash
        
        # Append to log file (JSONL format - one JSON per line)
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Update index
        index['total_entries'] += 1
        index['last_hash'] = event_hash
        index['last_updated'] = datetime.utcnow().isoformat()
        self._save_index(index)
        
        return event_id
    
    def log_analysis_started(self, record_id: str, 
                            input_file: str,
                            user_id: str = 'system') -> str:
        """Log when fraud analysis starts"""
        return self.log_event(
            event_type=AuditEventType.ANALYSIS_STARTED,
            record_id=record_id,
            details={
                'input_file': input_file,
                'action': 'Analysis initiated'
            },
            user_id=user_id
        )
    
    def log_analysis_completed(self, record_id: str,
                              result: Dict,
                              duration_seconds: float,
                              user_id: str = 'system') -> str:
        """Log when fraud analysis completes"""
        return self.log_event(
            event_type=AuditEventType.ANALYSIS_COMPLETED,
            record_id=record_id,
            details={
                'is_fraudulent': result.get('is_fraudulent'),
                'risk_score': result.get('risk_score'),
                'duration_seconds': duration_seconds,
                'ml_used': 'ml_predictions' in result,
                'action': 'Analysis completed'
            },
            user_id=user_id
        )
    
    def log_fraud_detected(self, record_id: str,
                          risk_score: float,
                          evidence_hash: str,
                          user_id: str = 'system') -> str:
        """Log when fraud is detected"""
        return self.log_event(
            event_type=AuditEventType.FRAUD_DETECTED,
            record_id=record_id,
            details={
                'risk_score': risk_score,
                'evidence_hash': evidence_hash,
                'severity': 'CRITICAL' if risk_score >= 75 else 'HIGH',
                'action': 'Fraud detected - evidence preserved'
            },
            user_id=user_id
        )
    
    def log_evidence_stored(self, record_id: str,
                           evidence_hash: str,
                           ipfs_cid: str = None,
                           storage_location: str = None,
                           user_id: str = 'system') -> str:
        """Log when evidence is stored"""
        return self.log_event(
            event_type=AuditEventType.EVIDENCE_STORED,
            record_id=record_id,
            details={
                'evidence_hash': evidence_hash,
                'ipfs_cid': ipfs_cid,
                'storage_location': storage_location,
                'action': 'Evidence stored immutably'
            },
            user_id=user_id
        )
    
    def log_evidence_retrieved(self, record_id: str,
                              evidence_hash: str,
                              retrieval_source: str,
                              user_id: str) -> str:
        """Log when evidence is retrieved"""
        return self.log_event(
            event_type=AuditEventType.EVIDENCE_RETRIEVED,
            record_id=record_id,
            details={
                'evidence_hash': evidence_hash,
                'retrieval_source': retrieval_source,
                'action': f'Evidence retrieved by {user_id}'
            },
            user_id=user_id
        )
    
    def log_error(self, record_id: str,
                  error_type: str,
                  error_message: str,
                  user_id: str = 'system') -> str:
        """Log when an error occurs"""
        return self.log_event(
            event_type=AuditEventType.ERROR_OCCURRED,
            record_id=record_id,
            details={
                'error_type': error_type,
                'error_message': error_message,
                'action': 'Error logged'
            },
            user_id=user_id
        )
    
    def get_events(self, 
                   record_id: str = None,
                   event_type: AuditEventType = None,
                   start_date: datetime = None,
                   end_date: datetime = None,
                   limit: int = 100) -> List[Dict]:
        """
        Retrieve audit events with filters
        
        Args:
            record_id: Filter by record ID
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of events to return
        
        Returns:
            List of matching audit events
        """
        events = []
        
        if not self.current_log_file.exists():
            return events
        
        with open(self.current_log_file, 'r') as f:
            for line in f:
                if len(events) >= limit:
                    break
                
                try:
                    event = json.loads(line.strip())
                    
                    # Apply filters
                    if record_id and event['record_id'] != record_id:
                        continue
                    
                    if event_type and event['event_type'] != event_type.value:
                        continue
                    
                    event_time = datetime.fromisoformat(event['timestamp'])
                    
                    if start_date and event_time < start_date:
                        continue
                    
                    if end_date and event_time > end_date:
                        continue
                    
                    events.append(event)
                
                except json.JSONDecodeError:
                    continue
        
        return events
    
    def get_record_history(self, record_id: str) -> List[Dict]:
        """Get complete audit history for a specific record"""
        return self.get_events(record_id=record_id, limit=1000)
    
    def verify_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of the entire audit trail
        
        Returns:
            Verification result
        """
        from hash_manager import HashManager
        
        hash_mgr = HashManager()
        
        if not self.current_log_file.exists():
            return {
                'is_valid': True,
                'message': 'No audit entries to verify'
            }
        
        events = []
        previous_hash = None
        corrupted_entries = []
        
        with open(self.current_log_file, 'r') as f:
            for i, line in enumerate(f):
                try:
                    event = json.loads(line.strip())
                    
                    # Check previous hash link
                    if event['previous_hash'] != previous_hash:
                        corrupted_entries.append({
                            'sequence': i + 1,
                            'event_id': event['event_id'],
                            'reason': 'Previous hash mismatch'
                        })
                    
                    # Verify event hash
                    stored_hash = event['event_hash']
                    event_copy = event.copy()
                    del event_copy['event_hash']
                    
                    calculated_hash = hash_mgr.hash_data(event_copy)
                    
                    if stored_hash != calculated_hash:
                        corrupted_entries.append({
                            'sequence': i + 1,
                            'event_id': event['event_id'],
                            'reason': 'Event hash mismatch'
                        })
                    
                    previous_hash = stored_hash
                    events.append(event)
                
                except json.JSONDecodeError:
                    corrupted_entries.append({
                        'sequence': i + 1,
                        'reason': 'Invalid JSON'
                    })
        
        is_valid = len(corrupted_entries) == 0
        
        return {
            'is_valid': is_valid,
            'total_entries': len(events),
            'corrupted_entries': corrupted_entries,
            'verified_at': datetime.utcnow().isoformat(),
            'status': 'VERIFIED' if is_valid else 'CORRUPTED'
        }
    
    def export_audit_log(self, output_path: str,
                        record_id: str = None,
                        format: str = 'json') -> str:
        """
        Export audit log to file
        
        Args:
            output_path: Output file path
            record_id: Filter by record ID (optional)
            format: 'json' or 'csv'
        
        Returns:
            Path to exported file
        """
        events = self.get_events(record_id=record_id, limit=10000)
        
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(events, f, indent=2)
        
        elif format == 'csv':
            import csv
            
            with open(output_path, 'w', newline='') as f:
                if events:
                    fieldnames = ['event_id', 'event_type', 'record_id', 
                                'timestamp', 'user_id', 'event_hash']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for event in events:
                        writer.writerow({
                            k: event.get(k, '') for k in fieldnames
                        })
        
        return output_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics"""
        index = self._load_index()
        
        events = self.get_events(limit=10000)
        
        # Count by event type
        event_type_counts = {}
        for event in events:
            event_type = event['event_type']
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Count by user
        user_counts = {}
        for event in events:
            user_id = event['user_id']
            user_counts[user_id] = user_counts.get(user_id, 0) + 1
        
        return {
            'total_entries': index['total_entries'],
            'created_at': index['created_at'],
            'last_updated': index.get('last_updated'),
            'event_type_counts': event_type_counts,
            'user_counts': user_counts,
            'unique_records': len(set(e['record_id'] for e in events))
        }


# Example usage
if __name__ == "__main__":
    print("📜 LandGuard Audit Trail Demo\n")
    
    # Initialize audit trail
    audit = AuditTrail()
    
    # Example 1: Log analysis workflow
    print("1️⃣ Logging Analysis Workflow")
    print("─" * 60)
    
    record_id = 'LAND_001'
    
    # Start analysis
    event_id = audit.log_analysis_started(
        record_id=record_id,
        input_file='suspicious_deed.pdf',
        user_id='analyst_123'
    )
    print(f"✅ Analysis started: {event_id}")
    
    # Complete analysis
    result = {
        'is_fraudulent': True,
        'risk_score': 87.5,
        'ml_predictions': {}
    }
    
    event_id = audit.log_analysis_completed(
        record_id=record_id,
        result=result,
        duration_seconds=2.5,
        user_id='analyst_123'
    )
    print(f"✅ Analysis completed: {event_id}")
    
    # Fraud detected
    event_id = audit.log_fraud_detected(
        record_id=record_id,
        risk_score=87.5,
        evidence_hash='abc123...',
        user_id='analyst_123'
    )
    print(f"🚨 Fraud detected: {event_id}")
    
    # Evidence stored
    event_id = audit.log_evidence_stored(
        record_id=record_id,
        evidence_hash='abc123...',
        ipfs_cid='Qm...',
        storage_location='IPFS+Local',
        user_id='system'
    )
    print(f"💾 Evidence stored: {event_id}\n")
    
    # Example 2: Retrieve history
    print("2️⃣ Retrieving Record History")
    print("─" * 60)
    
    history = audit.get_record_history(record_id)
    print(f"Found {len(history)} events for {record_id}:")
    
    for event in history:
        print(f"  • {event['event_type']:25s} | {event['timestamp']} | {event['user_id']}")
    
    # Example 3: Verify integrity
    print("\n3️⃣ Verifying Audit Trail Integrity")
    print("─" * 60)
    
    integrity = audit.verify_integrity()
    print(f"Status: {integrity['status']}")
    print(f"Total Entries: {integrity['total_entries']}")
    print(f"Is Valid: {'✅ Yes' if integrity['is_valid'] else '❌ No'}")
    
    if not integrity['is_valid']:
        print(f"Corrupted Entries: {len(integrity['corrupted_entries'])}")
    
    # Example 4: Statistics
    print("\n4️⃣ Audit Trail Statistics")
    print("─" * 60)
    
    stats = audit.get_statistics()
    print(f"Total Entries: {stats['total_entries']}")
    print(f"Unique Records: {stats['unique_records']}")
    print(f"\nEvent Type Distribution:")
    for event_type, count in stats['event_type_counts'].items():
        print(f"  • {event_type:25s}: {count}")
    
    # Example 5: Export
    print("\n5️⃣ Exporting Audit Log")
    print("─" * 60)
    
    export_path = audit.export_audit_log(
        'blockchain/storage/audit_logs/export.json',
        format='json'
    )
    print(f"📄 Exported to: {export_path}")
    
    print("\n✅ Audit Trail Demo Complete!")