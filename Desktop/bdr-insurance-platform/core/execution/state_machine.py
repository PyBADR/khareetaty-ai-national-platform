"""
Phase 2.3: Decision State Machine

Implements a strict state machine for decision lifecycle.
Enforces legal state transitions and decision finality.

Key Principles:
1. Only APPROVED decisions may EXECUTE
2. Only EXECUTED decisions may FINALIZE
3. FINALIZED decisions are IMMUTABLE
4. Illegal transitions raise exceptions
5. All transitions are audited
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List


class DecisionState(str, Enum):
    """Decision lifecycle states"""
    PROPOSED = "proposed"          # Decision created, not yet approved
    APPROVED = "approved"          # Decision approved, ready for execution
    EXECUTED = "executed"          # Decision executed, not yet final
    FINALIZED = "finalized"        # Decision finalized, IMMUTABLE
    REVOKED = "revoked"            # Decision revoked (if policy allows)


class StateTransitionError(Exception):
    """Base exception for state transition errors"""
    pass


class IllegalStateTransition(StateTransitionError):
    """Raised when attempting an illegal state transition"""
    pass


class FinalityViolation(StateTransitionError):
    """Raised when attempting to modify a FINALIZED decision"""
    pass


@dataclass
class StateTransition:
    """Record of a state transition"""
    from_state: DecisionState
    to_state: DecisionState
    transitioned_by: str
    transitioned_at: datetime
    reason: Optional[str] = None
    
    def to_audit_record(self) -> dict:
        return {
            "from_state": self.from_state.value,
            "to_state": self.to_state.value,
            "transitioned_by": self.transitioned_by,
            "transitioned_at": self.transitioned_at.isoformat(),
            "reason": self.reason,
        }


@dataclass
class DecisionStateMachine:
    """
    State machine for decision lifecycle management.
    
    Enforces:
    - Legal state transitions only
    - Finality immutability
    - Complete audit trail
    
    Legal Transitions:
    - PROPOSED → APPROVED
    - APPROVED → EXECUTED
    - EXECUTED → FINALIZED
    - APPROVED → REVOKED (if policy allows)
    - PROPOSED → REVOKED (if policy allows)
    
    Illegal Transitions:
    - PROPOSED → EXECUTED (must be approved first)
    - PROPOSED → FINALIZED (must be approved and executed first)
    - FINALIZED → * (finalized decisions are immutable)
    - * → PROPOSED (cannot go back to proposed)
    """
    decision_id: str
    current_state: DecisionState
    transition_history: List[StateTransition] = field(default_factory=list)
    allow_revocation: bool = True  # Policy: allow revoking decisions
    
    # Legal transition map
    LEGAL_TRANSITIONS = {
        DecisionState.PROPOSED: {DecisionState.APPROVED, DecisionState.REVOKED},
        DecisionState.APPROVED: {DecisionState.EXECUTED, DecisionState.REVOKED},
        DecisionState.EXECUTED: {DecisionState.FINALIZED},
        DecisionState.FINALIZED: set(),  # No transitions allowed from FINALIZED
        DecisionState.REVOKED: set(),    # No transitions allowed from REVOKED
    }
    
    def can_transition_to(self, target_state: DecisionState) -> bool:
        """
        Check if transition to target state is legal.
        
        Args:
            target_state: Desired target state
        
        Returns:
            True if transition is legal, False otherwise
        """
        # Check if transition is in legal transitions map
        legal_targets = self.LEGAL_TRANSITIONS.get(self.current_state, set())
        
        if target_state not in legal_targets:
            return False
        
        # Check revocation policy
        if target_state == DecisionState.REVOKED and not self.allow_revocation:
            return False
        
        return True
    
    def transition_to(
        self,
        target_state: DecisionState,
        transitioned_by: str,
        reason: Optional[str] = None,
    ) -> None:
        """
        Transition to a new state.
        
        Args:
            target_state: Desired target state
            transitioned_by: Authority ID performing transition
            reason: Optional reason for transition
        
        Raises:
            FinalityViolation: If attempting to modify FINALIZED decision
            IllegalStateTransition: If transition is not legal
        """
        # Check for finality violation
        if self.current_state == DecisionState.FINALIZED:
            raise FinalityViolation(
                f"Cannot transition from FINALIZED state. "
                f"Decision {self.decision_id} is immutable."
            )
        
        # Check if transition is legal
        if not self.can_transition_to(target_state):
            raise IllegalStateTransition(
                f"Illegal state transition: {self.current_state.value} → {target_state.value}. "
                f"Decision {self.decision_id} cannot transition to {target_state.value} "
                f"from {self.current_state.value}."
            )
        
        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=target_state,
            transitioned_by=transitioned_by,
            transitioned_at=datetime.now(timezone.utc),
            reason=reason,
        )
        
        self.transition_history.append(transition)
        self.current_state = target_state
    
    def is_finalized(self) -> bool:
        """Check if decision is finalized (immutable)"""
        return self.current_state == DecisionState.FINALIZED
    
    def is_revoked(self) -> bool:
        """Check if decision is revoked"""
        return self.current_state == DecisionState.REVOKED
    
    def can_execute(self) -> bool:
        """Check if decision can be executed"""
        return self.current_state == DecisionState.APPROVED
    
    def can_finalize(self) -> bool:
        """Check if decision can be finalized"""
        return self.current_state == DecisionState.EXECUTED
    
    def get_transition_history(self) -> List[dict]:
        """Get complete transition history for audit"""
        return [t.to_audit_record() for t in self.transition_history]
    
    def to_audit_record(self) -> dict:
        """Convert state machine to audit record"""
        return {
            "decision_id": self.decision_id,
            "current_state": self.current_state.value,
            "is_finalized": self.is_finalized(),
            "is_revoked": self.is_revoked(),
            "transition_count": len(self.transition_history),
            "transition_history": self.get_transition_history(),
        }


def create_state_machine(
    decision_id: str,
    initial_state: DecisionState = DecisionState.PROPOSED,
    allow_revocation: bool = True,
) -> DecisionStateMachine:
    """
    Create a new decision state machine.
    
    Args:
        decision_id: ID of the decision
        initial_state: Initial state (default: PROPOSED)
        allow_revocation: Whether to allow revoking decisions
    
    Returns:
        DecisionStateMachine instance
    """
    return DecisionStateMachine(
        decision_id=decision_id,
        current_state=initial_state,
        transition_history=[],
        allow_revocation=allow_revocation,
    )
