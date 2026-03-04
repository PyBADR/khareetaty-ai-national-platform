"""
Human Oversight Manager

Extracted from: insurance-hf-project/create_gradio_space.py
Purpose: Enforce human-in-the-loop controls and oversight requirements
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class OversightLevel(str, Enum):
    """Level of human oversight required"""
    NONE = "none"  # No human review needed (rare)
    ADVISORY = "advisory"  # Human reviews but system can proceed
    REQUIRED = "required"  # Human must approve before proceeding
    MANDATORY = "mandatory"  # Human must approve + provide justification
    ESCALATION = "escalation"  # Must escalate to senior authority


@dataclass
class OversightRequirement:
    """Defines oversight requirements for a decision"""
    level: OversightLevel
    justification_required: bool
    min_justification_length: int
    escalation_reason: Optional[str] = None
    additional_checks: List[str] = None
    
    def __post_init__(self):
        if self.additional_checks is None:
            self.additional_checks = []


@dataclass
class OversightRecord:
    """Record of human oversight action"""
    timestamp: datetime
    decision_id: str
    oversight_level: OversightLevel
    human_decision: str  # "approved", "rejected", "escalated", etc.
    justification: str
    reviewer_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class HumanOversightManager:
    """
    Manages human-in-the-loop oversight for decision-making.
    
    Key Principles:
    - Human has final decision authority
    - All outputs require human validation
    - Justification is mandatory for critical decisions
    - NO automatic approvals or rejections
    - NO autonomous decision-making
    """
    
    def __init__(self):
        self.oversight_records: List[OversightRecord] = []
        self.default_oversight_level = OversightLevel.REQUIRED
    
    def determine_oversight_level(self,
                                 risk_score: float,
                                 confidence: float,
                                 uncertainty_flag: bool,
                                 amount: Optional[float] = None,
                                 **kwargs) -> OversightRequirement:
        """
        Determine the level of human oversight required.
        
        Args:
            risk_score: Risk score (0-100)
            confidence: Model confidence (0-1)
            uncertainty_flag: Whether uncertainty is flagged
            amount: Financial amount involved
            **kwargs: Additional context
        
        Returns:
            OversightRequirement specifying oversight needs
        """
        # Default to mandatory oversight
        level = OversightLevel.MANDATORY
        justification_required = True
        min_length = 10
        escalation_reason = None
        additional_checks = []
        
        # High risk requires escalation
        if risk_score >= 80:
            level = OversightLevel.ESCALATION
            escalation_reason = f"High risk score: {risk_score}/100"
            min_length = 100
            additional_checks.append("Senior adjuster review")
            additional_checks.append("Additional investigation")
        
        # High uncertainty requires escalation
        elif uncertainty_flag or confidence < 0.6:
            level = OversightLevel.ESCALATION
            escalation_reason = f"High uncertainty (confidence: {confidence:.2%})"
            min_length = 50
            additional_checks.append("Specialist consultation")
        
        # Moderate risk requires mandatory justification
        elif risk_score >= 50 or confidence < 0.75:
            level = OversightLevel.MANDATORY
            min_length = 50
            additional_checks.append("Careful review of all evidence")
        
        # High-value claims require additional oversight
        if amount and amount > 50000:
            if level == OversightLevel.MANDATORY:
                level = OversightLevel.ESCALATION
                escalation_reason = f"High-value claim: ${amount:,.2f}"
            additional_checks.append("Financial review")
            min_length = max(min_length, 100)
        
        return OversightRequirement(
            level=level,
            justification_required=justification_required,
            min_justification_length=min_length,
            escalation_reason=escalation_reason,
            additional_checks=additional_checks
        )
    
    def validate_oversight_completion(self,
                                     requirement: OversightRequirement,
                                     justification: Optional[str] = None,
                                     human_decision: Optional[str] = None) -> tuple[bool, List[str]]:
        """
        Validate that oversight requirements have been met.
        
        Args:
            requirement: The oversight requirement to validate against
            justification: Human-provided justification
            human_decision: Human decision (approved/rejected/etc.)
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check if human decision is provided
        if not human_decision:
            errors.append("Human decision is required")
        
        # Check justification requirements
        if requirement.justification_required:
            if not justification or not justification.strip():
                errors.append("Human justification is required")
            elif len(justification.strip()) < requirement.min_justification_length:
                errors.append(
                    f"Justification must be at least {requirement.min_justification_length} characters. "
                    f"Current length: {len(justification.strip())}"
                )
        
        # Check escalation requirements
        if requirement.level == OversightLevel.ESCALATION:
            if not justification or 'escalat' not in justification.lower():
                errors.append(
                    f"This case requires escalation: {requirement.escalation_reason}. "
                    f"Please acknowledge escalation in your justification."
                )
        
        return len(errors) == 0, errors
    
    def record_oversight(self,
                        decision_id: str,
                        oversight_level: OversightLevel,
                        human_decision: str,
                        justification: str,
                        reviewer_id: Optional[str] = None,
                        **metadata) -> OversightRecord:
        """
        Record a human oversight action.
        
        Args:
            decision_id: Unique identifier for the decision
            oversight_level: Level of oversight applied
            human_decision: The human's decision
            justification: Human justification
            reviewer_id: ID of the human reviewer
            **metadata: Additional metadata to record
        
        Returns:
            OversightRecord
        """
        record = OversightRecord(
            timestamp=datetime.now(),
            decision_id=decision_id,
            oversight_level=oversight_level,
            human_decision=human_decision,
            justification=justification,
            reviewer_id=reviewer_id,
            metadata=metadata
        )
        
        self.oversight_records.append(record)
        return record
    
    def get_oversight_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of oversight actions.
        
        Returns:
            Dictionary with oversight statistics
        """
        if not self.oversight_records:
            return {
                'total_records': 0,
                'by_level': {},
                'by_decision': {}
            }
        
        by_level = {}
        by_decision = {}
        
        for record in self.oversight_records:
            # Count by oversight level
            level_str = record.oversight_level.value
            by_level[level_str] = by_level.get(level_str, 0) + 1
            
            # Count by decision type
            decision = record.human_decision
            by_decision[decision] = by_decision.get(decision, 0) + 1
        
        return {
            'total_records': len(self.oversight_records),
            'by_level': by_level,
            'by_decision': by_decision,
            'latest_timestamp': self.oversight_records[-1].timestamp.isoformat()
        }
    
    def format_oversight_notice(self, requirement: OversightRequirement) -> str:
        """
        Format a human-readable oversight notice.
        
        Args:
            requirement: Oversight requirement to format
        
        Returns:
            Formatted notice string
        """
        notice = f"\n## 👤 Human Oversight Required\n\n"
        notice += f"**Oversight Level**: {requirement.level.value.upper()}\n\n"
        
        if requirement.level == OversightLevel.ESCALATION:
            notice += f"### 🚨 ESCALATION REQUIRED\n"
            notice += f"**Reason**: {requirement.escalation_reason}\n\n"
        
        notice += "**This system does NOT make decisions automatically.**\n\n"
        notice += "The human reviewer must:\n"
        notice += "1. Review all decision signals and evidence\n"
        notice += "2. Apply professional judgment and expertise\n"
        notice += "3. Make the final decision\n"
        
        if requirement.justification_required:
            notice += f"4. Document justification (minimum {requirement.min_justification_length} characters)\n"
        
        if requirement.additional_checks:
            notice += "\n**Additional Requirements**:\n"
            for check in requirement.additional_checks:
                notice += f"- {check}\n"
        
        notice += "\n---\n\n"
        notice += "**Final Decision Authority**: Human Reviewer\n"
        notice += "**Model Role**: Advisory only\n"
        notice += "**Automation**: None - Human decision required\n"
        
        return notice
