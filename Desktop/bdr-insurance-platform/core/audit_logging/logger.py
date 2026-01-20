"""
Audit Logger

Extracted from: insurance-hf-project/create_gradio_space.py
Purpose: Comprehensive audit logging for all decision-making activities
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class AuditLevel(str, Enum):
    """Audit log severity level"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """
    Single audit log entry.
    
    Captures complete information about a decision or action for audit trail.
    """
    # Core identification
    timestamp: datetime
    entry_id: str
    entry_type: str  # "decision", "validation", "override", etc.
    level: AuditLevel = AuditLevel.INFO
    
    # Decision context
    decision_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Input data
    input_data: Dict[str, Any] = field(default_factory=dict)
    
    # Decision outputs
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Risk and confidence
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    confidence: Optional[float] = None
    uncertainty_flag: bool = False
    
    # Human oversight
    human_decision: Optional[str] = None
    human_justification: Optional[str] = None
    oversight_level: Optional[str] = None
    
    # Evidence and documentation
    missing_evidence: List[str] = field(default_factory=list)
    documentation_status: Optional[str] = None
    
    # Compliance
    compliance_status: Optional[str] = None
    compliance_violations: List[str] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # System information
    system_version: Optional[str] = None
    model_version: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit entry to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'entry_id': self.entry_id,
            'entry_type': self.entry_type,
            'level': self.level.value,
            'decision_id': self.decision_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'confidence': self.confidence,
            'uncertainty_flag': self.uncertainty_flag,
            'human_decision': self.human_decision,
            'human_justification': self.human_justification,
            'oversight_level': self.oversight_level,
            'missing_evidence': self.missing_evidence,
            'documentation_status': self.documentation_status,
            'compliance_status': self.compliance_status,
            'compliance_violations': self.compliance_violations,
            'metadata': self.metadata,
            'system_version': self.system_version,
            'model_version': self.model_version,
        }
    
    def to_json(self) -> str:
        """Convert audit entry to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def format_display(self) -> str:
        """
        Format audit entry for human-readable display.
        
        Returns:
            Formatted string for display
        """
        display = f"\n## Audit Log Entry\n\n"
        display += f"**Entry ID**: {self.entry_id}\n"
        display += f"**Timestamp**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        display += f"**Type**: {self.entry_type}\n"
        display += f"**Level**: {self.level.value.upper()}\n\n"
        
        if self.decision_id:
            display += f"**Decision ID**: {self.decision_id}\n"
        
        if self.user_id:
            display += f"**User**: {self.user_id}\n"
        
        display += "\n### Decision Metrics\n\n"
        
        if self.risk_score is not None:
            display += f"- **Risk Score**: {self.risk_score:.2f}\n"
        
        if self.risk_level:
            display += f"- **Risk Level**: {self.risk_level}\n"
        
        if self.confidence is not None:
            display += f"- **Confidence**: {self.confidence:.2%}\n"
        
        if self.uncertainty_flag:
            display += f"- **Uncertainty**: ⚠️ FLAGGED\n"
        
        if self.human_decision:
            display += f"\n### Human Decision\n\n"
            display += f"**Decision**: {self.human_decision}\n"
            
            if self.human_justification:
                display += f"\n**Justification**:\n{self.human_justification}\n"
        
        if self.missing_evidence:
            display += f"\n### Missing Evidence\n\n"
            for evidence in self.missing_evidence:
                display += f"- {evidence}\n"
        
        if self.compliance_violations:
            display += f"\n### Compliance Issues\n\n"
            for violation in self.compliance_violations:
                display += f"- ⚠️ {violation}\n"
        
        return display


class AuditLogger:
    """
    Audit logger for decision-making processes.
    
    Provides comprehensive audit trail with:
    - Complete input/output logging
    - Human decision tracking
    - Compliance verification
    - Risk and confidence metrics
    - Full traceability
    """
    
    def __init__(self, storage=None, system_version: str = "1.0.0"):
        """
        Initialize audit logger.
        
        Args:
            storage: AuditStorage implementation (defaults to in-memory)
            system_version: Version of the system for audit trail
        """
        from .storage import InMemoryAuditStorage
        
        self.storage = storage or InMemoryAuditStorage()
        self.system_version = system_version
        self._entry_counter = 0
    
    def _generate_entry_id(self) -> str:
        """Generate unique entry ID"""
        self._entry_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"AUD-{timestamp}-{self._entry_counter:06d}"
    
    def log_decision(self,
                    decision_id: str,
                    input_data: Dict[str, Any],
                    output_data: Dict[str, Any],
                    risk_score: Optional[float] = None,
                    risk_level: Optional[str] = None,
                    confidence: Optional[float] = None,
                    uncertainty_flag: bool = False,
                    human_decision: Optional[str] = None,
                    human_justification: Optional[str] = None,
                    oversight_level: Optional[str] = None,
                    missing_evidence: Optional[List[str]] = None,
                    user_id: Optional[str] = None,
                    **metadata) -> AuditEntry:
        """
        Log a decision with complete audit trail.
        
        Args:
            decision_id: Unique decision identifier
            input_data: Input data for the decision
            output_data: Output/result of the decision
            risk_score: Risk score (0-100)
            risk_level: Risk level (LOW/MEDIUM/HIGH)
            confidence: Model confidence (0-1)
            uncertainty_flag: Whether uncertainty is flagged
            human_decision: Human's final decision
            human_justification: Human's justification
            oversight_level: Level of oversight applied
            missing_evidence: List of missing evidence
            user_id: ID of the user making the decision
            **metadata: Additional metadata to log
        
        Returns:
            AuditEntry that was logged
        """
        entry = AuditEntry(
            timestamp=datetime.now(),
            entry_id=self._generate_entry_id(),
            entry_type="decision",
            level=AuditLevel.INFO,
            decision_id=decision_id,
            user_id=user_id,
            input_data=input_data,
            output_data=output_data,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            uncertainty_flag=uncertainty_flag,
            human_decision=human_decision,
            human_justification=human_justification,
            oversight_level=oversight_level,
            missing_evidence=missing_evidence or [],
            metadata=metadata,
            system_version=self.system_version
        )
        
        self.storage.store(entry)
        return entry
    
    def log_validation(self,
                      decision_id: str,
                      validation_type: str,
                      is_valid: bool,
                      errors: Optional[List[str]] = None,
                      warnings: Optional[List[str]] = None,
                      **metadata) -> AuditEntry:
        """
        Log a validation event.
        
        Args:
            decision_id: Decision being validated
            validation_type: Type of validation (input, justification, compliance)
            is_valid: Whether validation passed
            errors: List of validation errors
            warnings: List of validation warnings
            **metadata: Additional metadata
        
        Returns:
            AuditEntry that was logged
        """
        level = AuditLevel.ERROR if not is_valid else AuditLevel.INFO
        
        entry = AuditEntry(
            timestamp=datetime.now(),
            entry_id=self._generate_entry_id(),
            entry_type="validation",
            level=level,
            decision_id=decision_id,
            output_data={
                'validation_type': validation_type,
                'is_valid': is_valid,
                'errors': errors or [],
                'warnings': warnings or []
            },
            metadata=metadata,
            system_version=self.system_version
        )
        
        self.storage.store(entry)
        return entry
    
    def log_compliance_check(self,
                           decision_id: str,
                           is_compliant: bool,
                           violations: Optional[List[str]] = None,
                           **metadata) -> AuditEntry:
        """
        Log a compliance check.
        
        Args:
            decision_id: Decision being checked
            is_compliant: Whether decision is compliant
            violations: List of compliance violations
            **metadata: Additional metadata
        
        Returns:
            AuditEntry that was logged
        """
        level = AuditLevel.CRITICAL if not is_compliant else AuditLevel.INFO
        
        entry = AuditEntry(
            timestamp=datetime.now(),
            entry_id=self._generate_entry_id(),
            entry_type="compliance_check",
            level=level,
            decision_id=decision_id,
            compliance_status="compliant" if is_compliant else "non_compliant",
            compliance_violations=violations or [],
            metadata=metadata,
            system_version=self.system_version
        )
        
        self.storage.store(entry)
        return entry
    
    def log_override(self,
                    decision_id: str,
                    original_recommendation: str,
                    human_override: str,
                    justification: str,
                    user_id: Optional[str] = None,
                    **metadata) -> AuditEntry:
        """
        Log when a human overrides a system recommendation.
        
        Args:
            decision_id: Decision being overridden
            original_recommendation: System's original recommendation
            human_override: Human's override decision
            justification: Justification for override
            user_id: ID of user performing override
            **metadata: Additional metadata
        
        Returns:
            AuditEntry that was logged
        """
        entry = AuditEntry(
            timestamp=datetime.now(),
            entry_id=self._generate_entry_id(),
            entry_type="override",
            level=AuditLevel.WARNING,
            decision_id=decision_id,
            user_id=user_id,
            output_data={
                'original_recommendation': original_recommendation,
                'human_override': human_override
            },
            human_decision=human_override,
            human_justification=justification,
            metadata=metadata,
            system_version=self.system_version
        )
        
        self.storage.store(entry)
        return entry
    
    def get_entries(self,
                   decision_id: Optional[str] = None,
                   user_id: Optional[str] = None,
                   entry_type: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[AuditEntry]:
        """
        Retrieve audit entries with optional filtering.
        
        Args:
            decision_id: Filter by decision ID
            user_id: Filter by user ID
            entry_type: Filter by entry type
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            limit: Maximum number of entries to return
        
        Returns:
            List of matching audit entries
        """
        return self.storage.query(
            decision_id=decision_id,
            user_id=user_id,
            entry_type=entry_type,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    
    def get_decision_trail(self, decision_id: str) -> List[AuditEntry]:
        """
        Get complete audit trail for a specific decision.
        
        Args:
            decision_id: Decision ID to retrieve trail for
        
        Returns:
            List of all audit entries for this decision
        """
        return self.storage.query(decision_id=decision_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.storage.get_statistics()
    
    def export_entries(self,
                      decision_id: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      format: str = "json") -> str:
        """
        Export audit entries in specified format.
        
        Args:
            decision_id: Filter by decision ID
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            format: Export format ("json" or "csv")
        
        Returns:
            Exported data as string
        """
        entries = self.get_entries(
            decision_id=decision_id,
            start_time=start_time,
            end_time=end_time
        )
        
        if format == "json":
            return json.dumps([e.to_dict() for e in entries], indent=2)
        elif format == "csv":
            # Simple CSV export
            import csv
            from io import StringIO
            
            output = StringIO()
            if entries:
                writer = csv.DictWriter(output, fieldnames=entries[0].to_dict().keys())
                writer.writeheader()
                for entry in entries:
                    writer.writerow(entry.to_dict())
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
