"""
Human Action Contract - Signed Decision Actions

Human-in-the-loop is NOT a boolean. It is a signed event.
This module defines the contract for human decision actions with full accountability.

Author: BDR Platform Team
Created: 2026-01-20
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class HumanActionType(str, Enum):
    """Types of human actions on decisions"""
    APPROVE = "approve"  # Human approves the decision
    REJECT = "reject"  # Human rejects the decision
    OVERRIDE = "override"  # Human overrides the decision with new values
    REQUEST_INFO = "request_info"  # Human requests additional information
    ESCALATE = "escalate"  # Human escalates to higher authority
    DEFER = "defer"  # Human defers decision to later time
    ACKNOWLEDGE = "acknowledge"  # Human acknowledges but takes no action


class RejectionReasonCode(str, Enum):
    """Standardized rejection reason codes"""
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    POLICY_VIOLATION = "policy_violation"
    REGULATORY_CONCERN = "regulatory_concern"
    RISK_TOO_HIGH = "risk_too_high"
    INCOMPLETE_DATA = "incomplete_data"
    CONFLICTING_INFORMATION = "conflicting_information"
    OUTSIDE_AUTHORITY = "outside_authority"
    REQUIRES_SPECIALIST = "requires_specialist"
    FRAUD_SUSPECTED = "fraud_suspected"
    CUSTOMER_DISPUTE = "customer_dispute"
    OTHER = "other"


class OverrideJustificationType(str, Enum):
    """Types of justification for overrides"""
    BUSINESS_EXCEPTION = "business_exception"
    CUSTOMER_RELATIONSHIP = "customer_relationship"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    RISK_MITIGATION = "risk_mitigation"
    POLICY_INTERPRETATION = "policy_interpretation"
    EXTENUATING_CIRCUMSTANCES = "extenuating_circumstances"
    SYSTEM_ERROR_CORRECTION = "system_error_correction"
    EXPERT_JUDGMENT = "expert_judgment"


class HumanDecisionAction(BaseModel):
    """
    Human Decision Action - Signed event for human intervention
    
    Rules:
    - Overrides MUST include justification
    - Rejections MUST include reason codes
    - Approved decisions generate immutable artifacts
    - Actions are append-only (no mutation)
    """
    
    # Action identification
    action_id: str = Field(..., description="Unique action identifier")
    action_type: HumanActionType = Field(..., description="Type of human action")
    linked_decision_id: str = Field(..., description="Decision ID this action applies to")
    
    # Actor information
    actor_id: str = Field(..., min_length=1, description="Unique identifier of the human actor")
    actor_role: str = Field(..., min_length=1, description="Role of the actor (e.g., 'Claims Adjuster', 'Underwriting Manager')")
    actor_name: Optional[str] = Field(None, description="Name of the actor (optional for privacy)")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the action was taken")
    
    # Justification (mandatory for certain actions)
    justification: str = Field(..., min_length=10, description="Human-readable justification for this action")
    
    # Action-specific fields
    rejection_reason_code: Optional[RejectionReasonCode] = Field(
        None,
        description="Standardized reason code (required for REJECT actions)"
    )
    override_justification_type: Optional[OverrideJustificationType] = Field(
        None,
        description="Type of justification (required for OVERRIDE actions)"
    )
    override_values: Optional[Dict[str, Any]] = Field(
        None,
        description="New values for override (required for OVERRIDE actions)"
    )
    requested_information: Optional[List[str]] = Field(
        None,
        description="List of information requested (for REQUEST_INFO actions)"
    )
    escalation_target_role: Optional[str] = Field(
        None,
        description="Role to escalate to (for ESCALATE actions)"
    )
    defer_until: Optional[datetime] = Field(
        None,
        description="When to revisit decision (for DEFER actions)"
    )
    
    # Audit trail
    ip_address: Optional[str] = Field(None, description="IP address of the actor (for audit)")
    session_id: Optional[str] = Field(None, description="Session ID (for audit)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Immutability
    is_final: bool = Field(
        default=False,
        description="Whether this action is final and cannot be superseded"
    )
    supersedes_action_id: Optional[str] = Field(
        None,
        description="Previous action ID that this action supersedes"
    )
    
    @field_validator('action_type')
    @classmethod
    def validate_action_requirements(cls, v: HumanActionType, info) -> HumanActionType:
        """Validate that required fields are present for each action type"""
        # Note: Full validation happens in model_validator since we need access to all fields
        return v
    
    def model_post_init(self, __context) -> None:
        """Validate action-specific requirements after model initialization"""
        # REJECT actions must have rejection_reason_code
        if self.action_type == HumanActionType.REJECT and not self.rejection_reason_code:
            raise ValueError("REJECT actions must include rejection_reason_code")
        
        # OVERRIDE actions must have override_justification_type and override_values
        if self.action_type == HumanActionType.OVERRIDE:
            if not self.override_justification_type:
                raise ValueError("OVERRIDE actions must include override_justification_type")
            if not self.override_values:
                raise ValueError("OVERRIDE actions must include override_values")
        
        # REQUEST_INFO actions must have requested_information
        if self.action_type == HumanActionType.REQUEST_INFO and not self.requested_information:
            raise ValueError("REQUEST_INFO actions must include requested_information list")
        
        # ESCALATE actions must have escalation_target_role
        if self.action_type == HumanActionType.ESCALATE and not self.escalation_target_role:
            raise ValueError("ESCALATE actions must include escalation_target_role")
        
        # DEFER actions must have defer_until
        if self.action_type == HumanActionType.DEFER and not self.defer_until:
            raise ValueError("DEFER actions must include defer_until timestamp")
    
    def is_approval(self) -> bool:
        """Check if this action approves the decision"""
        return self.action_type == HumanActionType.APPROVE
    
    def is_rejection(self) -> bool:
        """Check if this action rejects the decision"""
        return self.action_type == HumanActionType.REJECT
    
    def is_override(self) -> bool:
        """Check if this action overrides the decision"""
        return self.action_type == HumanActionType.OVERRIDE
    
    def requires_follow_up(self) -> bool:
        """Check if this action requires follow-up"""
        return self.action_type in [
            HumanActionType.REQUEST_INFO,
            HumanActionType.ESCALATE,
            HumanActionType.DEFER
        ]
    
    def is_terminal(self) -> bool:
        """Check if this action terminates the decision process"""
        return self.action_type in [
            HumanActionType.APPROVE,
            HumanActionType.REJECT
        ] or (self.action_type == HumanActionType.OVERRIDE and self.is_final)
    
    def to_audit_log(self) -> Dict[str, Any]:
        """Convert to audit log format"""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "linked_decision_id": self.linked_decision_id,
            "actor_id": self.actor_id,
            "actor_role": self.actor_role,
            "timestamp": self.timestamp.isoformat(),
            "justification": self.justification,
            "is_final": self.is_final,
            "is_terminal": self.is_terminal(),
            "metadata": self.metadata
        }
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "action_id": "action-2026-01-20-xyz789",
                    "action_type": "approve",
                    "linked_decision_id": "fnol-2026-01-20-abc123",
                    "actor_id": "adjuster-12345",
                    "actor_role": "Senior Claims Adjuster",
                    "justification": "Claim is well-documented with clear liability. All policy conditions met.",
                    "is_final": True
                },
                {
                    "action_id": "action-2026-01-20-xyz790",
                    "action_type": "reject",
                    "linked_decision_id": "fnol-2026-01-20-abc124",
                    "actor_id": "adjuster-12346",
                    "actor_role": "Claims Adjuster",
                    "justification": "Insufficient evidence to support claim. Medical records incomplete and witness statements conflict.",
                    "rejection_reason_code": "insufficient_evidence",
                    "is_final": True
                },
                {
                    "action_id": "action-2026-01-20-xyz791",
                    "action_type": "override",
                    "linked_decision_id": "fnol-2026-01-20-abc125",
                    "actor_id": "manager-98765",
                    "actor_role": "Claims Manager",
                    "justification": "Long-standing customer with excellent history. Business relationship justifies exception to standard triage.",
                    "override_justification_type": "customer_relationship",
                    "override_values": {
                        "priority": "HIGH",
                        "assigned_adjuster": "senior-adjuster-001"
                    },
                    "is_final": False
                }
            ]
        }


class HumanActionChain(BaseModel):
    """
    Chain of human actions on a decision
    
    Maintains append-only history of all human interventions.
    """
    
    decision_id: str = Field(..., description="Decision ID this chain belongs to")
    actions: List[HumanDecisionAction] = Field(
        default_factory=list,
        description="Ordered list of actions (append-only)"
    )
    
    def add_action(self, action: HumanDecisionAction) -> None:
        """
        Add a new action to the chain
        
        Args:
            action: Human action to add
            
        Raises:
            ValueError: If chain is already finalized or action is invalid
        """
        if action.linked_decision_id != self.decision_id:
            raise ValueError(f"Action decision_id {action.linked_decision_id} does not match chain decision_id {self.decision_id}")
        
        if self.is_finalized():
            raise ValueError(f"Cannot add action to finalized decision {self.decision_id}")
        
        self.actions.append(action)
    
    def get_latest_action(self) -> Optional[HumanDecisionAction]:
        """Get the most recent action"""
        return self.actions[-1] if self.actions else None
    
    def get_terminal_action(self) -> Optional[HumanDecisionAction]:
        """Get the terminal action (if any)"""
        for action in reversed(self.actions):
            if action.is_terminal():
                return action
        return None
    
    def is_finalized(self) -> bool:
        """Check if the decision chain is finalized"""
        terminal = self.get_terminal_action()
        return terminal is not None and terminal.is_final
    
    def is_approved(self) -> bool:
        """Check if the decision is approved"""
        terminal = self.get_terminal_action()
        return terminal is not None and terminal.is_approval()
    
    def is_rejected(self) -> bool:
        """Check if the decision is rejected"""
        terminal = self.get_terminal_action()
        return terminal is not None and terminal.is_rejection()
    
    def has_overrides(self) -> bool:
        """Check if the decision has any overrides"""
        return any(action.is_override() for action in self.actions)
    
    def get_override_count(self) -> int:
        """Get the number of overrides"""
        return sum(1 for action in self.actions if action.is_override())
    
    def get_all_actors(self) -> List[str]:
        """Get list of all actors who touched this decision"""
        return list(set(action.actor_id for action in self.actions))
    
    def to_audit_trail(self) -> List[Dict[str, Any]]:
        """Convert entire chain to audit trail format"""
        return [action.to_audit_log() for action in self.actions]


# Factory functions for common actions

def create_approval_action(
    action_id: str,
    decision_id: str,
    actor_id: str,
    actor_role: str,
    justification: str,
    is_final: bool = True
) -> HumanDecisionAction:
    """Create a standard approval action"""
    return HumanDecisionAction(
        action_id=action_id,
        action_type=HumanActionType.APPROVE,
        linked_decision_id=decision_id,
        actor_id=actor_id,
        actor_role=actor_role,
        justification=justification,
        is_final=is_final
    )


def create_rejection_action(
    action_id: str,
    decision_id: str,
    actor_id: str,
    actor_role: str,
    justification: str,
    reason_code: RejectionReasonCode,
    is_final: bool = True
) -> HumanDecisionAction:
    """Create a standard rejection action"""
    return HumanDecisionAction(
        action_id=action_id,
        action_type=HumanActionType.REJECT,
        linked_decision_id=decision_id,
        actor_id=actor_id,
        actor_role=actor_role,
        justification=justification,
        rejection_reason_code=reason_code,
        is_final=is_final
    )


def create_override_action(
    action_id: str,
    decision_id: str,
    actor_id: str,
    actor_role: str,
    justification: str,
    justification_type: OverrideJustificationType,
    override_values: Dict[str, Any],
    is_final: bool = False
) -> HumanDecisionAction:
    """Create a standard override action"""
    return HumanDecisionAction(
        action_id=action_id,
        action_type=HumanActionType.OVERRIDE,
        linked_decision_id=decision_id,
        actor_id=actor_id,
        actor_role=actor_role,
        justification=justification,
        override_justification_type=justification_type,
        override_values=override_values,
        is_final=is_final
    )
