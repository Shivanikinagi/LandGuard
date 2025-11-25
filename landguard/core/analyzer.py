"""
LandGuard Fraud Detection Analyzer
Orchestrates all fraud detection rules and generates comprehensive anomaly reports.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    from difflib import SequenceMatcher
    RAPIDFUZZ_AVAILABLE = False

from core.models import LandRecord, Transaction, OwnerHistory, AnomalyReport, Issue
from core.config import get_config


class LandGuardAnalyzer:
    """Main fraud detection engine that runs all checks with configuration support."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Optional configuration dict to override defaults
        """
        # Load global config or use defaults
        self.global_config = get_config()
        
        # Override with provided config if any
        if config:
            self.global_config.update(config)
        
        # Internal indexes for duplicate detection
        self.land_id_index: Dict[str, List[str]] = defaultdict(list)
        self.transaction_index: Dict[str, str] = {}
    
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
        
        # Run enabled detection rules
        if self.global_config.get('enable_missing_field_detection', True):
            issues.extend(self._check_missing_fields(record))
        
        if self.global_config.get('enable_duplicate_detection', True):
            issues.extend(self._check_duplicate_land_id(record))
        
        if self.global_config.get('enable_rapid_transfer_detection', True):
            issues.extend(self._check_rapid_transfers(record))
        
        if self.global_config.get('enable_time_order_detection', True):
            issues.extend(self._check_time_order(record))
        
        if self.global_config.get('enable_party_mismatch_detection', True):
            issues.extend(self._check_party_mismatches(record))
        
        if self.global_config.get('enable_large_transfer_detection', True):
            issues.extend(self._check_large_transfers(record))
        
        if self.global_config.get('enable_duplicate_detection', True):
            issues.extend(self._check_duplicate_transactions(record))
        
        # Cross-document conflict checks (if historical records provided)
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
        """Check for suspiciously rapid ownership transfers using configured thresholds."""
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
        
        # Get configuration
        rapid_days = self.global_config.get('rapid_transfer_days', 180)
        rapid_count = self.global_config.get('rapid_transfer_count', 2)
        
        transfer_count = 0
        window_start = None
        involved_owners = []
        
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i - 1]
            curr = sorted_history[i]
            
            days_diff = (curr.date - prev.date).days
            
            if days_diff <= rapid_days:
                if window_start is None:
                    window_start = prev.date
                    transfer_count = 2
                    involved_owners = [prev.owner_name, curr.owner_name]
                else:
                    transfer_count += 1
                    involved_owners.append(curr.owner_name)
                
                if transfer_count >= rapid_count:
                    issues.append(Issue(
                        type="rapid_transfer",
                        message=f"Ownership changed {transfer_count} times within {rapid_days} days",
                        severity="high",
                        evidence=[
                            f"Window start: {window_start.isoformat()}",
                            f"Current transfer: {curr.date.isoformat()}",
                            f"Owners involved: {' → '.join(involved_owners)}"
                        ],
                        field="owner_history",
                        date_range=(window_start.isoformat(), curr.date.isoformat())
                    ))
                    break  # Report once per window
            else:
                # Reset window
                window_start = None
                transfer_count = 0
                involved_owners = []
        
        return issues
    
    def _check_time_order(self, record: LandRecord) -> List[Issue]:
        """Check that dates in owner history are in chronological order."""
        issues = []
        
        if not record.owner_history:
            return issues
        
        dated_history = [oh for oh in record.owner_history if oh.date]
        
        if len(dated_history) < 2:
            return issues
        
        tolerance_days = self.global_config.get('date_order_tolerance_days', 1)
        tolerance = timedelta(days=tolerance_days)
        
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
        """Check if transaction parties match owner history using configured similarity threshold."""
        issues = []
        
        if not record.transactions or not record.owner_history:
            return issues
        
        # Build owner timeline
        owner_timeline = {}
        for oh in sorted(record.owner_history, key=lambda x: x.date if x.date else datetime.min):
            if oh.date:
                owner_timeline[oh.date] = oh.owner_name
        
        # Get similarity threshold from config
        similarity_threshold = self.global_config.get('name_similarity_threshold', 85)
        
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
                similarity = self._calculate_name_similarity(
                    tx.from_party,
                    expected_owner
                )
                
                if similarity < similarity_threshold:
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
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity percentage."""
        if RAPIDFUZZ_AVAILABLE:
            return fuzz.ratio(name1.lower().strip(), name2.lower().strip())
        else:
            # Fallback to difflib
            similarity = SequenceMatcher(
                None, 
                name1.lower().strip(), 
                name2.lower().strip()
            ).ratio()
            return similarity * 100
    
    def _check_large_transfers(self, record: LandRecord) -> List[Issue]:
        """Flag unusually large financial transfers using configured threshold."""
        issues = []
        
        if not record.transactions:
            return issues
        
        threshold = self.global_config.get('large_transfer_threshold', 10000000)
        
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
        Analyze multiple records as a batch with cross-document checks.
        
        Args:
            records: List of land records to analyze
            report_path: Optional path to save consolidated report
            
        Returns:
            List of anomaly reports
        """
        reports = []
        
        # Use configured batch size
        batch_size = self.global_config.get('batch_size', 100)
        
        for i, record in enumerate(records):
            # Pass previously analyzed records for cross-document checks
            historical = records[:i]
            report = self.analyze_record(record, historical)
            reports.append(report)
            
            # Progress logging if verbose enabled
            if self.global_config.get('enable_verbose', False):
                if (i + 1) % batch_size == 0:
                    print(f"Processed {i + 1}/{len(records)} records...")
        
        if report_path:
            self._save_batch_report(reports, report_path)
        
        return reports
    
    def _save_batch_report(self, reports: List[AnomalyReport], path: str):
        """Save consolidated batch report in configured format."""
        output_format = self.global_config.get('output_format', 'json')
        
        consolidated = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_records": len(reports),
            "total_issues": sum(r.total_issues for r in reports),
            "high_severity_count": sum(1 for r in reports if r.highest_severity == "high"),
            "medium_severity_count": sum(1 for r in reports if r.highest_severity == "medium"),
            "low_severity_count": sum(1 for r in reports if r.highest_severity == "low"),
            "reports": [r.dict() for r in reports]
        }
        
        output_path = Path(path)
        
        if output_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(consolidated, f, indent=2)
        elif output_format == 'text':
            self._save_text_report(consolidated, output_path)
        elif output_format == 'csv':
            self._save_csv_report(reports, output_path)
    
    def _save_text_report(self, consolidated: Dict, path: Path):
        """Save report in human-readable text format."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("LandGuard Batch Analysis Report\n")
            f.write("="*60 + "\n\n")
            f.write(f"Generated: {consolidated['generated_at']}\n")
            f.write(f"Total Records: {consolidated['total_records']}\n")
            f.write(f"Total Issues: {consolidated['total_issues']}\n")
            f.write(f"High Severity: {consolidated['high_severity_count']}\n")
            f.write(f"Medium Severity: {consolidated['medium_severity_count']}\n")
            f.write(f"Low Severity: {consolidated['low_severity_count']}\n\n")
            
            for report_data in consolidated['reports']:
                if report_data['total_issues'] > 0:
                    f.write("-"*60 + "\n")
                    f.write(f"Record ID: {report_data['record_id']}\n")
                    f.write(f"Source: {report_data['source_file']}\n")
                    f.write(f"Issues: {report_data['total_issues']}\n")
                    f.write(f"Severity: {report_data['highest_severity']}\n\n")
                    
                    for issue in report_data['issues']:
                        f.write(f"  • {issue['type']}: {issue['message']}\n")
                        f.write(f"    Severity: {issue['severity']}\n")
                        for evidence in issue.get('evidence', []):
                            f.write(f"    - {evidence}\n")
                        f.write("\n")
    
    def _save_csv_report(self, reports: List[AnomalyReport], path: Path):
        """Save report in CSV format."""
        import csv
        
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Record ID', 'Source File', 'Issue Type', 'Severity',
                'Message', 'Field', 'Evidence Count'
            ])
            
            for report in reports:
                for issue in report.issues:
                    writer.writerow([
                        report.record_id,
                        report.source_file,
                        issue.type,
                        issue.severity,
                        issue.message,
                        issue.field or '',
                        len(issue.evidence) if issue.evidence else 0
                    ])

"""
Land fraud detection analyzer with configurable rules.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict

from core.models import LandRecord, Transaction, Issue, AnomalyReport
from core.config import get_config


class LandGuardAnalyzer:
    """Main analyzer for land fraud detection."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize analyzer with configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or get_config().to_dict()
        
        # Extract thresholds from config
        self.rapid_transfer_days = self.config.get('fraud_detection', {}).get('rapid_transfer_days', 90)
        self.rapid_transfer_count = self.config.get('fraud_detection', {}).get('rapid_transfer_count', 3)
        self.suspicious_amount = self.config.get('fraud_detection', {}).get('suspicious_amount_threshold', 10000000)
    
    def analyze_record(self, record: LandRecord) -> AnomalyReport:
        """
        Analyze a single land record for fraud indicators.
        
        Args:
            record: Land record to analyze
            
        Returns:
            AnomalyReport with detected issues
        """
        issues = []
        
        # Run all detection methods
        issues.extend(self._check_missing_fields(record))
        issues.extend(self._check_rapid_transfers(record))
        issues.extend(self._check_party_mismatches(record))
        issues.extend(self._check_large_transfers(record))
        issues.extend(self._check_time_order(record))
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(issues)
        
        # Determine if fraud detected
        fraud_detected = risk_score >= self.config.get('fraud_detection', {}).get('min_risk_score', 50)
        
        return AnomalyReport(
            land_id=record.land_id,
            fraud_detected=fraud_detected,
            issues=issues,
            risk_score=risk_score,
            metadata={
                'total_issues': len(issues),
                'high_severity': sum(1 for i in issues if i.severity == 'high'),
                'medium_severity': sum(1 for i in issues if i.severity == 'medium'),
                'low_severity': sum(1 for i in issues if i.severity == 'low'),
                'source_file': getattr(record, 'source_file', None)
            }
        )
    
    def _check_missing_fields(self, record: LandRecord) -> List[Issue]:
        """Check for missing required fields."""
        issues = []
        
        if not record.owner_history:
            issues.append(Issue(
                type='missing_owner_history',
                severity='high',
                description='No owner history found for this land record',
                details={'land_id': record.land_id}
            ))
        
        if not record.transactions:
            issues.append(Issue(
                type='missing_transactions',
                severity='medium',
                description='No transaction history found',
                details={'land_id': record.land_id}
            ))
        
        return issues
    
    def _check_rapid_transfers(self, record: LandRecord) -> List[Issue]:
        """Detect rapid ownership changes."""
        issues = []
        
        if len(record.owner_history) < 2:
            return issues
        
        # Sort by date
        sorted_history = sorted(record.owner_history, key=lambda x: x.date)
        
        # Check for rapid changes in time window
        for i in range(len(sorted_history) - 1):
            time_diff = (sorted_history[i + 1].date - sorted_history[i].date).days
            
            if time_diff < self.rapid_transfer_days:
                issues.append(Issue(
                    type='rapid_ownership_change',
                    severity='high',
                    description=f'Ownership changed within {time_diff} days',
                    details={
                        'from_owner': sorted_history[i].owner_name,
                        'to_owner': sorted_history[i + 1].owner_name,
                        'days_between': time_diff,
                        'threshold': self.rapid_transfer_days
                    }
                ))
        
        # Check total changes in time window
        if len(sorted_history) >= self.rapid_transfer_count:
            first_date = sorted_history[0].date
            last_date = sorted_history[-1].date
            days_span = (last_date - first_date).days
            
            if days_span < self.rapid_transfer_days * self.rapid_transfer_count:
                issues.append(Issue(
                    type='multiple_rapid_transfers',
                    severity='critical',
                    description=f'{len(sorted_history)} ownership changes in {days_span} days',
                    details={
                        'change_count': len(sorted_history),
                        'days_span': days_span,
                        'threshold_days': self.rapid_transfer_days
                    }
                ))
        
        return issues
    
    def _check_party_mismatches(self, record: LandRecord) -> List[Issue]:
        """Check for mismatches between transactions and owner history."""
        issues = []
        
        if not record.transactions or not record.owner_history:
            return issues
        
        # Build owner timeline
        owners = {owner.date: owner.owner_name for owner in record.owner_history}
        
        for tx in record.transactions:
            # Check if transaction parties match owner history
            expected_owner = None
            for owner_date, owner_name in sorted(owners.items()):
                if owner_date <= tx.date:
                    expected_owner = owner_name
                else:
                    break
            
            if expected_owner and tx.from_party != expected_owner:
                issues.append(Issue(
                    type='party_mismatch',
                    severity='high',
                    description=f'Transaction from party does not match expected owner',
                    details={
                        'transaction_date': tx.date.isoformat(),
                        'from_party': tx.from_party,
                        'expected_owner': expected_owner,
                        'transaction_id': getattr(tx, 'tx_id', None)
                    }
                ))
        
        return issues
    
    def _check_large_transfers(self, record: LandRecord) -> List[Issue]:
        """Detect unusually large transaction amounts."""
        issues = []
        
        for tx in record.transactions:
            if tx.amount and tx.amount > self.suspicious_amount:
                issues.append(Issue(
                    type='large_transaction',
                    severity='medium',
                    description=f'Transaction amount exceeds threshold',
                    details={
                        'amount': tx.amount,
                        'threshold': self.suspicious_amount,
                        'from_party': tx.from_party,
                        'to_party': tx.to_party,
                        'date': tx.date.isoformat()
                    }
                ))
        
        return issues
    
    def _check_time_order(self, record: LandRecord) -> List[Issue]:
        """Check for time ordering conflicts."""
        issues = []
        
        if not record.transactions or not record.owner_history:
            return issues
        
        # Check if transactions occur before ownership
        for tx in record.transactions:
            # Find the owner at transaction time
            prior_owners = [o for o in record.owner_history if o.date <= tx.date]
            if not prior_owners:
                issues.append(Issue(
                    type='temporal_conflict',
                    severity='high',
                    description='Transaction occurred before any recorded ownership',
                    details={
                        'transaction_date': tx.date.isoformat(),
                        'from_party': tx.from_party,
                        'to_party': tx.to_party
                    }
                ))
        
        return issues
    
    def _calculate_risk_score(self, issues: List[Issue]) -> float:
        """
        Calculate overall risk score based on issues.
        
        Args:
            issues: List of detected issues
            
        Returns:
            Risk score between 0 and 100
        """
        if not issues:
            return 0.0
        
        # Severity weights
        weights = {
            'critical': 40,
            'high': 25,
            'medium': 15,
            'low': 5
        }
        
        total_score = sum(weights.get(issue.severity, 0) for issue in issues)
        
        # Cap at 100
        return min(total_score, 100.0)
    
    def analyze_batch(self, records: List[LandRecord]) -> List[AnomalyReport]:
        """
        Analyze multiple records.
        
        Args:
            records: List of land records
            
        Returns:
            List of anomaly reports
        """
        return [self.analyze_record(record) for record in records]
    
    def get_statistics(self, reports: List[AnomalyReport]) -> Dict[str, Any]:
        """
        Generate statistics from analysis reports.
        
        Args:
            reports: List of anomaly reports
            
        Returns:
            Statistics dictionary
        """
        total = len(reports)
        fraud_detected = sum(1 for r in reports if r.fraud_detected)
        
        # Risk score distribution
        high_risk = sum(1 for r in reports if r.risk_score >= 70)
        medium_risk = sum(1 for r in reports if 40 <= r.risk_score < 70)
        low_risk = sum(1 for r in reports if r.risk_score < 40)
        
        # Issue type distribution
        issue_types = defaultdict(int)
        for report in reports:
            for issue in report.issues:
                issue_types[issue.type] += 1
        
        return {
            'total_records': total,
            'fraud_detected_count': fraud_detected,
            'fraud_rate': round(fraud_detected / total * 100, 2) if total > 0 else 0,
            'risk_distribution': {
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            },
            'issue_types': dict(issue_types),
            'average_risk_score': round(sum(r.risk_score for r in reports) / total, 2) if total > 0 else 0
        }