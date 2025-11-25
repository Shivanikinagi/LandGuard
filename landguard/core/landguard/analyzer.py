"""
LandGuard Fraud Detection Analyzer
Orchestrates all fraud detection rules and generates comprehensive anomaly reports.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
from rapidfuzz import fuzz

from ..models import LandRecord, Transaction, OwnerHistory, AnomalyReport, Issue


class LandGuardAnalyzer:
    """Main fraud detection engine that runs all checks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Configuration dict with thresholds and settings
        """
        self.config = config or self._default_config()
        self.land_id_index: Dict[str, List[str]] = defaultdict(list)  # land_id -> [file_uuids]
        self.transaction_index: Dict[str, str] = {}  # tx_id -> file_uuid
        
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "rapid_transfer_days": 180,
            "rapid_transfer_count": 2,
            "large_transfer_threshold": 10000000,  # 10M in local currency
            "name_similarity_threshold": 85,  # % similarity for fuzzy matching
            "date_order_tolerance_days": 1,  # Allow 1 day tolerance for date ordering
        }
    
    def analyze_record(
        self, 
        record: LandRecord,
        historical_records: Optional[List[LandRecord]] = None
    ) -> AnomalyReport:
        """
        Run all fraud detection checks on a land record.
        
        Args:
            record: The land record to analyze
            historical_records: Previously processed records for cross-document checks
            
        Returns:
            AnomalyReport with all detected issues
        """
        issues: List[Issue] = []
        
        # 1. Check for missing mandatory fields
        issues.extend(self._check_missing_fields(record))
        
        # 2. Check for duplicate land IDs
        issues.extend(self._check_duplicate_land_id(record))
        
        # 3. Check for rapid ownership transfers
        issues.extend(self._check_rapid_transfers(record))
        
        # 4. Check for time order conflicts in owner history
        issues.extend(self._check_time_order(record))
        
        # 5. Check for party mismatches in transactions
        issues.extend(self._check_party_mismatches(record))
        
        # 6. Check for large transfers
        issues.extend(self._check_large_transfers(record))
        
        # 7. Check for duplicate transaction IDs
        issues.extend(self._check_duplicate_transactions(record))
        
        # 8. Cross-document conflict checks (if historical records provided)
        if historical_records:
            issues.extend(self._check_cross_document_conflicts(record, historical_records))
        
        # Calculate overall confidence score
        confidence = self._calculate_confidence(issues)
        
        # Update indexes
        self._update_indexes(record)
        
        return AnomalyReport(
            record_id=record.land_id,
            source_file=record.source_file or "unknown",
            issues=issues,
            confidence=confidence,
            generated_at=datetime.utcnow().isoformat(),
            total_issues=len(issues),
            highest_severity=self._get_highest_severity(issues),
            extracted_summary=self._create_summary(record)
        )
    
    def _check_missing_fields(self, record: LandRecord) -> List[Issue]:
        """Check for missing mandatory fields."""
        issues = []
        
        if not record.land_id:
            issues.append(Issue(
                type="missing_field",
                message="Missing mandatory field: land_id",
                severity="high",
                evidence=["land_id field is null or empty"],
                field="land_id"
            ))
        
        if not record.owner_history or len(record.owner_history) == 0:
            issues.append(Issue(
                type="missing_field",
                message="Missing or empty owner_history",
                severity="high",
                evidence=["owner_history is missing or has no entries"],
                field="owner_history"
            ))
        
        return issues
    
    def _check_duplicate_land_id(self, record: LandRecord) -> List[Issue]:
        """Check if land_id already exists in the index."""
        issues = []
        
        if record.land_id in self.land_id_index:
            existing_files = self.land_id_index[record.land_id]
            issues.append(Issue(
                type="duplicate_land_id",
                message=f"Land ID {record.land_id} already exists in {len(existing_files)} other file(s)",
                severity="high",
                evidence=[
                    f"Duplicate found in: {', '.join(existing_files[:3])}",
                    f"Current file: {record.source_file}"
                ],
                field="land_id"
            ))
        
        return issues
    
    def _check_rapid_transfers(self, record: LandRecord) -> List[Issue]:
        """Check for suspiciously rapid ownership transfers."""
        issues = []
        
        if not record.owner_history or len(record.owner_history) < 2:
            return issues
        
        # Sort by date
        sorted_history = sorted(
            [oh for oh in record.owner_history if oh.date],
            key=lambda x: x.date
        )
        
        if len(sorted_history) < 2:
            return issues
        
        # Check consecutive transfers
        rapid_days = self.config["rapid_transfer_days"]
        rapid_count = self.config["rapid_transfer_count"]
        
        transfer_count = 0
        window_start = None
        
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i - 1]
            curr = sorted_history[i]
            
            days_diff = (curr.date - prev.date).days
            
            if days_diff <= rapid_days:
                if window_start is None:
                    window_start = prev.date
                    transfer_count = 2
                else:
                    transfer_count += 1
                
                if transfer_count >= rapid_count:
                    issues.append(Issue(
                        type="rapid_transfer",
                        message=f"Ownership changed {transfer_count} times within {rapid_days} days",
                        severity="high",
                        evidence=[
                            f"Window start: {window_start.isoformat()}",
                            f"Current transfer: {curr.date.isoformat()}",
                            f"Owners involved: {prev.owner_name} → {curr.owner_name}"
                        ],
                        field="owner_history",
                        date_range=(window_start.isoformat(), curr.date.isoformat())
                    ))
                    break  # Report once per window
            else:
                # Reset window
                window_start = None
                transfer_count = 0
        
        return issues
    
    def _check_time_order(self, record: LandRecord) -> List[Issue]:
        """Check that dates in owner history are in ascending order."""
        issues = []
        
        if not record.owner_history:
            return issues
        
        dated_history = [oh for oh in record.owner_history if oh.date]
        
        if len(dated_history) < 2:
            return issues
        
        tolerance = timedelta(days=self.config["date_order_tolerance_days"])
        
        for i in range(1, len(dated_history)):
            prev = dated_history[i - 1]
            curr = dated_history[i]
            
            # Allow slight tolerance for same-day transfers
            if curr.date < prev.date - tolerance:
                issues.append(Issue(
                    type="time_order_conflict",
                    message="Owner history dates are not in chronological order",
                    severity="medium",
                    evidence=[
                        f"Entry {i - 1}: {prev.owner_name} at {prev.date.isoformat()}",
                        f"Entry {i}: {curr.owner_name} at {curr.date.isoformat()}",
                        "Later entry has earlier date"
                    ],
                    field="owner_history"
                ))
        
        return issues
    
    def _check_party_mismatches(self, record: LandRecord) -> List[Issue]:
        """Check if transaction parties match owner history."""
        issues = []
        
        if not record.transactions or not record.owner_history:
            return issues
        
        # Build owner timeline
        owner_timeline = {}
        for oh in sorted(record.owner_history, key=lambda x: x.date if x.date else datetime.min):
            if oh.date:
                owner_timeline[oh.date] = oh.owner_name
        
        # Check each transaction
        for tx in record.transactions:
            if not tx.date or not tx.from_party:
                continue
            
            # Find the owner at transaction date
            expected_owner = None
            for date in sorted(owner_timeline.keys()):
                if date <= tx.date:
                    expected_owner = owner_timeline[date]
                else:
                    break
            
            if expected_owner:
                # Use fuzzy matching for name comparison
                similarity = fuzz.ratio(
                    tx.from_party.lower().strip(),
                    expected_owner.lower().strip()
                )
                
                if similarity < self.config["name_similarity_threshold"]:
                    issues.append(Issue(
                        type="party_mismatch",
                        message=f"Transaction 'from' party doesn't match recorded owner",
                        severity="high",
                        evidence=[
                            f"Transaction ID: {tx.tx_id}",
                            f"Date: {tx.date.isoformat()}",
                            f"Transaction from: {tx.from_party}",
                            f"Expected owner: {expected_owner}",
                            f"Similarity: {similarity}%"
                        ],
                        field="transactions",
                        transaction_id=tx.tx_id
                    ))
        
        return issues
    
    def _check_large_transfers(self, record: LandRecord) -> List[Issue]:
        """Flag unusually large financial transfers."""
        issues = []
        
        if not record.transactions:
            return issues
        
        threshold = self.config["large_transfer_threshold"]
        
        for tx in record.transactions:
            if tx.amount and tx.amount >= threshold:
                issues.append(Issue(
                    type="large_transfer",
                    message=f"Unusually large transfer amount: {tx.amount:,}",
                    severity="medium",
                    evidence=[
                        f"Transaction ID: {tx.tx_id}",
                        f"Amount: {tx.amount:,}",
                        f"Date: {tx.date.isoformat() if tx.date else 'unknown'}",
                        f"From: {tx.from_party} → To: {tx.to_party}",
                        f"Threshold: {threshold:,}"
                    ],
                    field="transactions",
                    transaction_id=tx.tx_id,
                    amount=tx.amount
                ))
        
        return issues
    
    def _check_duplicate_transactions(self, record: LandRecord) -> List[Issue]:
        """Check for duplicate transaction IDs."""
        issues = []
        
        if not record.transactions:
            return issues
        
        seen_tx_ids = set()
        
        for tx in record.transactions:
            if not tx.tx_id:
                continue
            
            # Check within current record
            if tx.tx_id in seen_tx_ids:
                issues.append(Issue(
                    type="duplicate_transaction",
                    message=f"Duplicate transaction ID within same record: {tx.tx_id}",
                    severity="high",
                    evidence=[
                        f"Transaction ID: {tx.tx_id}",
                        f"Found multiple times in {record.source_file}"
                    ],
                    field="transactions",
                    transaction_id=tx.tx_id
                ))
            
            # Check against historical index
            if tx.tx_id in self.transaction_index:
                existing_file = self.transaction_index[tx.tx_id]
                issues.append(Issue(
                    type="duplicate_transaction",
                    message=f"Transaction ID already exists in another file",
                    severity="high",
                    evidence=[
                        f"Transaction ID: {tx.tx_id}",
                        f"Current file: {record.source_file}",
                        f"Previous file: {existing_file}"
                    ],
                    field="transactions",
                    transaction_id=tx.tx_id
                ))
            
            seen_tx_ids.add(tx.tx_id)
        
        return issues
    
    def _check_cross_document_conflicts(
        self, 
        record: LandRecord, 
        historical_records: List[LandRecord]
    ) -> List[Issue]:
        """Check for conflicts across different documents for same land_id."""
        issues = []
        
        for historical in historical_records:
            if historical.land_id != record.land_id:
                continue
            
            # Check property area conflicts
            if (record.property_area and historical.property_area and 
                abs(record.property_area - historical.property_area) > 0.01):
                issues.append(Issue(
                    type="data_mismatch",
                    message="Property area mismatch between documents",
                    severity="high",
                    evidence=[
                        f"Current file: {record.source_file}, Area: {record.property_area}",
                        f"Historical file: {historical.source_file}, Area: {historical.property_area}"
                    ],
                    field="property_area"
                ))
            
            # Check registration number conflicts
            if (record.registration_number and historical.registration_number and
                record.registration_number != historical.registration_number):
                issues.append(Issue(
                    type="data_mismatch",
                    message="Registration number mismatch between documents",
                    severity="high",
                    evidence=[
                        f"Current: {record.registration_number}",
                        f"Historical: {historical.registration_number}"
                    ],
                    field="registration_number"
                ))
        
        return issues
    
    def _calculate_confidence(self, issues: List[Issue]) -> float:
        """Calculate overall confidence score based on issues found."""
        if not issues:
            return 1.0
        
        # Weight by severity
        severity_weights = {"low": 0.05, "medium": 0.15, "high": 0.30}
        
        total_weight = sum(severity_weights.get(issue.severity, 0.1) for issue in issues)
        
        # Clamp to [0, 1] range
        confidence = max(0.0, min(1.0, 1.0 - total_weight))
        
        return round(confidence, 3)
    
    def _get_highest_severity(self, issues: List[Issue]) -> str:
        """Get the highest severity level from issues."""
        if not issues:
            return "none"
        
        severity_order = {"high": 3, "medium": 2, "low": 1}
        
        highest = max(issues, key=lambda x: severity_order.get(x.severity, 0))
        return highest.severity
    
    def _create_summary(self, record: LandRecord) -> Dict[str, Any]:
        """Create a summary of the record for reporting."""
        return {
            "land_id": record.land_id,
            "owner_count": len(record.owner_history) if record.owner_history else 0,
            "transaction_count": len(record.transactions) if record.transactions else 0,
            "property_area": record.property_area,
            "registration_number": record.registration_number,
            "source_file": record.source_file
        }
    
    def _update_indexes(self, record: LandRecord):
        """Update internal indexes for duplicate detection."""
        if record.land_id:
            self.land_id_index[record.land_id].append(record.source_file or "unknown")
        
        if record.transactions:
            for tx in record.transactions:
                if tx.tx_id:
                    self.transaction_index[tx.tx_id] = record.source_file or "unknown"
    
    def batch_analyze(
        self, 
        records: List[LandRecord],
        report_path: Optional[str] = None
    ) -> List[AnomalyReport]:
        """
        Analyze multiple records as a batch.
        
        Args:
            records: List of land records to analyze
            report_path: Optional path to save consolidated report
            
        Returns:
            List of anomaly reports
        """
        reports = []
        
        for i, record in enumerate(records):
            # Pass previously analyzed records for cross-document checks
            historical = records[:i]
            report = self.analyze_record(record, historical)
            reports.append(report)
        
        if report_path:
            self._save_batch_report(reports, report_path)
        
        return reports
    
    def _save_batch_report(self, reports: List[AnomalyReport], path: str):
        """Save consolidated batch report."""
        import json
        
        consolidated = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_records": len(reports),
            "total_issues": sum(r.total_issues for r in reports),
            "high_severity_count": sum(1 for r in reports if r.highest_severity == "high"),
            "reports": [r.dict() for r in reports]
        }
        
        with open(path, 'w') as f:
            json.dump(consolidated, f, indent=2)