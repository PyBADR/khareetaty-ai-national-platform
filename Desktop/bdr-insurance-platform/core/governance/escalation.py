"""Escalation Workflows Module

This module implements automatic escalation workflows for decisions that:
- Exceed authority limits
- Fail production gates
- Require higher-level approval
- Trigger compliance violations

All escalations are tracked, auditable, and enforceable.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4

from .authority import DecisionAuthority, DecisionSeverity
from .ownership import DecisionOwner, AccountabilityChain
from .production_gates import ProductionGateResult, GateStatus


class EscalationTrigger(Enum):
    """Triggers that cause a decision to be escalated."""
    AUTHORITY_EXCEEDED = "authority_exceeded"  # Decision exceeds authority limits
    GATE_FAILED = "gate_failed"  # Production gate failed
    SEVERITY_THRESHOLD = "severity_threshold"  # Severity exceeds threshold
    COMPLIANCE_VIOLATION = "compliance_violation"  # Compliance check failed
    MANUAL_ESCALATION = "manual_escalation"  # Manually escalated by user
    TIMEOUT = "timeout"  # Decision timed out waiting for approval
    BOUNDARY_VIOLATION = "boundary_violation"  # Decision violates boundaries
    RISK_THRESHOLD = "risk_threshold"  # Risk score exceeds threshold


class EscalationStatus(Enum):
    """Status of an escalation."""
    PENDING = "pending"  # Escalation pending review
    APPROVED = "approved"  # Escalation approved, decision can proceed
    REJECTED = "rejected"  # Escalation rejected, decision blocked
    TIMEOUT = "timeout"  # Escalation timed out
    CANCELLED = "cancelled"  # Escalation cancelled


class EscalationPriority(Enum):
    """Priority level for escalations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


@dataclass(frozen=True)
class EscalationPath:
    """Defines an escalation path for decisions.
    
    Attributes:
        path_id: Unique identifier for this escalation path
        trigger: What triggers this escalation
        from_authority: Authority that triggered the escalation
        to_owner: Owner who should review the escalation
        priority: Priority level of the escalation
        timeout_hours: Hours before escalation times out
        requires_approval: Whether explicit approval is required
        can_auto_approve: Whether escalation can be auto-approved
        auto_approve_conditions: Conditions for auto-approval
        notification_channels: Channels to notify (email, slack, etc.)
        metadata: Additional escalation metadata
    """
    path_id: str
    trigger: EscalationTrigger
    from_authority: DecisionAuthority
    to_owner: DecisionOwner
    priority: EscalationPriority
    timeout_hours: int
    requires_approval: bool
    can_auto_approve: bool
    auto_approve_conditions: Dict[str, Any] = field(default_factory=dict)
    notification_channels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate escalation path."""
        if not self.path_id:
            raise ValueError("path_id cannot be empty")
        if self.timeout_hours <= 0:
            raise ValueError("timeout_hours must be positive")
        if self.can_auto_approve and not self.auto_approve_conditions:
            raise ValueError("Auto-approve requires conditions")


@dataclass(frozen=True)
class EscalationRequest:
    """Request for decision escalation.
    
    Attributes:
        escalation_id: Unique identifier for this escalation
        decision_id: ID of the decision being escalated
        trigger: What triggered the escalation
        triggered_by: Who/what triggered the escalation
        triggered_at: When the escalation was triggered
        escalation_path: Path this escalation follows
        current_authority: Current authority (insufficient)
        required_authority: Required authority to proceed
        reason: Detailed reason for escalation
        context: Additional context for the escalation
        gate_failures: Failed gates (if applicable)
        metadata: Additional escalation metadata
    """
    escalation_id: str
    decision_id: str
    trigger: EscalationTrigger
    triggered_by: str
    triggered_at: datetime
    escalation_path: EscalationPath
    current_authority: DecisionAuthority
    required_authority: Optional[DecisionAuthority]
    reason: str
    context: Dict[str, Any] = field(default_factory=dict)
    gate_failures: List[ProductionGateResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate escalation request."""
        if not self.escalation_id:
            raise ValueError("escalation_id cannot be empty")
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty")
        if not self.reason:
            raise ValueError("reason cannot be empty")


@dataclass(frozen=True)
class EscalationResponse:
    """Response to an escalation request.
    
    Attributes:
        escalation_id: ID of the escalation being responded to
        status: Status of the escalation
        reviewed_by: Who reviewed the escalation
        reviewed_at: When the escalation was reviewed
        approved_authority: Authority granted (if approved)
        rejection_reason: Reason for rejection (if rejected)
        conditions: Conditions attached to approval (if any)
        expires_at: When the approval expires (if applicable)
        metadata: Additional response metadata
    """
    escalation_id: str
    status: EscalationStatus
    reviewed_by: str
    reviewed_at: datetime
    approved_authority: Optional[DecisionAuthority] = None
    rejection_reason: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate escalation response."""
        if not self.escalation_id:
            raise ValueError("escalation_id cannot be empty")
        
        # If approved, must have approved_authority
        if self.status == EscalationStatus.APPROVED and not self.approved_authority:
            raise ValueError("Approved escalation must have approved_authority")
        
        # If rejected, must have rejection_reason
        if self.status == EscalationStatus.REJECTED and not self.rejection_reason:
            raise ValueError("Rejected escalation must have rejection_reason")


def create_escalation_path(
    trigger: EscalationTrigger,
    from_authority: DecisionAuthority,
    to_owner: DecisionOwner,
    priority: EscalationPriority = EscalationPriority.MEDIUM,
    timeout_hours: int = 24,
    requires_approval: bool = True,
    can_auto_approve: bool = False,
    auto_approve_conditions: Optional[Dict[str, Any]] = None,
    notification_channels: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> EscalationPath:
    """Create an escalation path.
    
    Args:
        trigger: What triggers this escalation
        from_authority: Authority that triggered the escalation
        to_owner: Owner who should review the escalation
        priority: Priority level
        timeout_hours: Hours before timeout
        requires_approval: Whether approval is required
        can_auto_approve: Whether auto-approval is allowed
        auto_approve_conditions: Conditions for auto-approval
        notification_channels: Notification channels
        metadata: Additional metadata
    
    Returns:
        EscalationPath instance
    """
    path_id = f"escalation_path_{trigger.value}_{uuid4().hex[:8]}"
    
    return EscalationPath(
        path_id=path_id,
        trigger=trigger,
        from_authority=from_authority,
        to_owner=to_owner,
        priority=priority,
        timeout_hours=timeout_hours,
        requires_approval=requires_approval,
        can_auto_approve=can_auto_approve,
        auto_approve_conditions=auto_approve_conditions or {},
        notification_channels=notification_channels or ["email"],
        metadata=metadata or {}
    )


def escalate_decision(
    decision_id: str,
    trigger: EscalationTrigger,
    current_authority: DecisionAuthority,
    escalation_path: EscalationPath,
    reason: str,
    required_authority: Optional[DecisionAuthority] = None,
    context: Optional[Dict[str, Any]] = None,
    gate_failures: Optional[List[ProductionGateResult]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> EscalationRequest:
    """Escalate a decision for higher-level review.
    
    Args:
        decision_id: ID of the decision to escalate
        trigger: What triggered the escalation
        current_authority: Current (insufficient) authority
        escalation_path: Path to follow for escalation
        reason: Reason for escalation
        required_authority: Required authority to proceed
        context: Additional context
        gate_failures: Failed gates (if applicable)
        metadata: Additional metadata
    
    Returns:
        EscalationRequest instance
    """
    escalation_id = f"escalation_{decision_id}_{uuid4().hex[:8]}"
    triggered_by = current_authority.authority_id
    
    return EscalationRequest(
        escalation_id=escalation_id,
        decision_id=decision_id,
        trigger=trigger,
        triggered_by=triggered_by,
        triggered_at=datetime.utcnow(),
        escalation_path=escalation_path,
        current_authority=current_authority,
        required_authority=required_authority,
        reason=reason,
        context=context or {},
        gate_failures=gate_failures or [],
        metadata=metadata or {}
    )


def should_escalate(
    decision_severity: DecisionSeverity,
    authority: DecisionAuthority,
    gate_results: Optional[List[ProductionGateResult]] = None
) -> tuple[bool, Optional[EscalationTrigger], Optional[str]]:
    """Determine if a decision should be escalated.
    
    Args:
        decision_severity: Severity of the decision
        authority: Authority attempting the decision
        gate_results: Results of production gate evaluations
    
    Returns:
        Tuple of (should_escalate, trigger, reason)
    """
    # Check if severity exceeds authority
    severity_order = [
        DecisionSeverity.ROUTINE,
        DecisionSeverity.ELEVATED,
        DecisionSeverity.CRITICAL,
        DecisionSeverity.EMERGENCY,
        DecisionSeverity.CATASTROPHIC,
    ]
    
    decision_level = severity_order.index(decision_severity)
    authority_level = severity_order.index(authority.max_decision_severity)
    
    if decision_level > authority_level:
        reason = f"Decision severity {decision_severity.value} exceeds authority limit {authority.max_decision_severity.value}"
        return True, EscalationTrigger.AUTHORITY_EXCEEDED, reason
    
    # Check for gate failures
    if gate_results:
        failed_gates = [gr for gr in gate_results if gr.status == GateStatus.FAILED]
        if failed_gates:
            gate_names = ", ".join([gr.gate.name for gr in failed_gates])
            reason = f"Production gates failed: {gate_names}"
            return True, EscalationTrigger.GATE_FAILED, reason
    
    # Check if human signature required but not present
    if authority.requires_human_signature:
        # This would need to check if signature is actually present
        # For now, we assume it's handled elsewhere
        pass
    
    return False, None, None


def get_escalation_priority(
    trigger: EscalationTrigger,
    decision_severity: DecisionSeverity
) -> EscalationPriority:
    """Determine escalation priority based on trigger and severity.
    
    Args:
        trigger: What triggered the escalation
        decision_severity: Severity of the decision
    
    Returns:
        Appropriate escalation priority
    """
    # Critical triggers always get high priority
    if trigger in (EscalationTrigger.COMPLIANCE_VIOLATION, EscalationTrigger.BOUNDARY_VIOLATION):
        return EscalationPriority.CRITICAL
    
    # Map severity to priority
    severity_to_priority = {
        DecisionSeverity.ROUTINE: EscalationPriority.LOW,
        DecisionSeverity.ELEVATED: EscalationPriority.MEDIUM,
        DecisionSeverity.CRITICAL: EscalationPriority.HIGH,
        DecisionSeverity.EMERGENCY: EscalationPriority.URGENT,
        DecisionSeverity.CATASTROPHIC: EscalationPriority.CRITICAL,
    }
    
    return severity_to_priority.get(decision_severity, EscalationPriority.MEDIUM)


def resolve_escalation_target(
    current_authority: DecisionAuthority,
    ownership_chain: AccountabilityChain
) -> DecisionOwner:
    """Determine who should review an escalation.
    
    Args:
        current_authority: Current (insufficient) authority
        ownership_chain: Ownership chain for the decision
    
    Returns:
        Owner who should review the escalation
    """
    # First try escalation owner
    if ownership_chain.escalation_owner:
        return ownership_chain.escalation_owner
    
    # Fall back to ultimate accountable
    return ownership_chain.ultimate_accountable