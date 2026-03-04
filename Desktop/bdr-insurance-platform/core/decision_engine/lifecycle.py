"""
Decision Lifecycle - State Machine for Decision Governance

Explicit state management for insurance decisions.
No skipping states. No silent transitions.

Author: BDR Platform Team
Created: 2026-01-20
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DecisionState(str, Enum):
    """
    Decision lifecycle states
    
    State transition rules:
    - DRAFT -> EVALUATED (after initial processing)
    - EVALUATED -> REQUIRES_HUMAN (if boundaries fail or policy requires)
    - EVALUATED -> APPROVED (if actionable and no human review needed)
    - REQUIRES_HUMAN -> APPROVED (after human approval)
    - REQUIRES_HUMAN -> REJECTED (after human rejection)
    - REQUIRES_HUMAN -> OVERRIDDEN (after human override)
    - REQUIRES_HUMAN -> ESCALATED (if beyond authority)
    - ESCALATED -> APPROVED/REJECTED/OVERRIDDEN (after escalation resolution)
    - APPROVED/REJECTED/OVERRIDDEN -> FINALIZED (after all actions complete)
    
    Terminal states: FINALIZED
    Blocking states: ESCALATED (blocks automation)
    """
    DRAFT = "draft"  # Initial state, decision being constructed
    EVALUATED = "evaluated"  # Decision has been evaluated by system
    REQUIRES_HUMAN = "requires_human"  # Decision requires human review
    APPROVED = "approved"  # Decision approved (by system or human)
    REJECTED = "rejected"  # Decision rejected by human
    OVERRIDDEN = "overridden"  # Decision overridden by human
    ESCALATED = "escalated"  # Decision escalated to higher authority
    FINALIZED = "finalized"  # Decision is final and immutable


class StateTransition(BaseModel):
    """Record of a state transition"""
    
    from_state: DecisionState = Field(..., description="Previous state")
    to_state: DecisionState = Field(..., description="New state")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When transition occurred")
    triggered_by: str = Field(..., description="What triggered this transition (system/actor_id)")
    reason: str = Field(..., description="Human-readable reason for transition")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional transition metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_state": "evaluated",
                "to_state": "requires_human",
                "triggered_by": "system",
                "reason": "Claim amount $75,000 exceeds monetary boundary threshold",
                "metadata": {"boundary_type": "monetary", "threshold": 50000, "actual": 75000}
            }
        }


class DecisionLifecycle(BaseModel):
    """
    Decision Lifecycle Manager
    
    Enforces state machine rules:
    - No skipping states
    - OVERRIDE cannot jump directly to FINALIZED
    - ESCALATED decisions block automation
    - All transitions are logged
    """
    
    decision_id: str = Field(..., description="Decision ID this lifecycle tracks")
    current_state: DecisionState = Field(
        default=DecisionState.DRAFT,
        description="Current state of the decision"
    )
    state_history: List[StateTransition] = Field(
        default_factory=list,
        description="Complete history of state transitions"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the decision lifecycle started"
    )
    finalized_at: Optional[datetime] = Field(
        None,
        description="When the decision was finalized (if applicable)"
    )
    
    # Valid state transitions (from_state -> [allowed_to_states])
    _VALID_TRANSITIONS: Dict[DecisionState, List[DecisionState]] = {
        DecisionState.DRAFT: [DecisionState.EVALUATED],
        DecisionState.EVALUATED: [
            DecisionState.REQUIRES_HUMAN,
            DecisionState.APPROVED,
            DecisionState.FINALIZED  # Direct finalization if no human review needed
        ],
        DecisionState.REQUIRES_HUMAN: [
            DecisionState.APPROVED,
            DecisionState.REJECTED,
            DecisionState.OVERRIDDEN,
            DecisionState.ESCALATED
        ],
        DecisionState.APPROVED: [DecisionState.FINALIZED],
        DecisionState.REJECTED: [DecisionState.FINALIZED],
        DecisionState.OVERRIDDEN: [
            DecisionState.APPROVED,  # Override must be approved before finalization
            DecisionState.REQUIRES_HUMAN,  # Override may require additional review
            DecisionState.ESCALATED  # Override may trigger escalation
        ],
        DecisionState.ESCALATED: [
            DecisionState.APPROVED,
            DecisionState.REJECTED,
            DecisionState.OVERRIDDEN
        ],
        DecisionState.FINALIZED: []  # Terminal state, no transitions allowed
    }
    
    def transition_to(
        self,
        new_state: DecisionState,
        triggered_by: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Transition to a new state
        
        Args:
            new_state: Target state
            triggered_by: What/who triggered this transition
            reason: Human-readable reason
            metadata: Additional metadata
            
        Raises:
            ValueError: If transition is not allowed
        """
        # Check if transition is valid
        if not self._is_valid_transition(self.current_state, new_state):
            raise ValueError(
                f"Invalid state transition: {self.current_state.value} -> {new_state.value}. "
                f"Allowed transitions from {self.current_state.value}: "
                f"{[s.value for s in self._VALID_TRANSITIONS.get(self.current_state, [])]}"
            )
        
        # Record transition
        transition = StateTransition(
            from_state=self.current_state,
            to_state=new_state,
            triggered_by=triggered_by,
            reason=reason,
            metadata=metadata or {}
        )
        self.state_history.append(transition)
        
        # Update current state
        self.current_state = new_state
        
        # Set finalized timestamp if reaching terminal state
        if new_state == DecisionState.FINALIZED:
            self.finalized_at = datetime.utcnow()
    
    def _is_valid_transition(self, from_state: DecisionState, to_state: DecisionState) -> bool:
        """Check if a state transition is valid"""
        allowed_states = self._VALID_TRANSITIONS.get(from_state, [])
        return to_state in allowed_states
    
    def is_terminal(self) -> bool:
        """Check if decision is in terminal state"""
        return self.current_state == DecisionState.FINALIZED
    
    def is_blocking_automation(self) -> bool:
        """Check if current state blocks automation"""
        return self.current_state in [
            DecisionState.REQUIRES_HUMAN,
            DecisionState.ESCALATED
        ]
    
    def requires_human_action(self) -> bool:
        """Check if decision requires human action"""
        return self.current_state in [
            DecisionState.REQUIRES_HUMAN,
            DecisionState.ESCALATED,
            DecisionState.OVERRIDDEN  # Overrides may require approval
        ]
    
    def can_be_finalized(self) -> bool:
        """Check if decision can be finalized"""
        return self.current_state in [
            DecisionState.APPROVED,
            DecisionState.REJECTED,
            DecisionState.EVALUATED  # Can finalize directly if no human review needed
        ]
    
    def get_time_in_current_state(self) -> float:
        """Get time spent in current state (in seconds)"""
        if not self.state_history:
            # Still in initial DRAFT state
            return (datetime.utcnow() - self.created_at).total_seconds()
        
        last_transition = self.state_history[-1]
        return (datetime.utcnow() - last_transition.timestamp).total_seconds()
    
    def get_total_lifecycle_time(self) -> float:
        """Get total time from creation to now/finalization (in seconds)"""
        end_time = self.finalized_at or datetime.utcnow()
        return (end_time - self.created_at).total_seconds()
    
    def get_state_durations(self) -> Dict[str, float]:
        """Get time spent in each state (in seconds)"""
        durations: Dict[str, float] = {}
        
        if not self.state_history:
            # Only been in DRAFT state
            durations[DecisionState.DRAFT.value] = self.get_time_in_current_state()
            return durations
        
        # Time in DRAFT (before first transition)
        first_transition = self.state_history[0]
        durations[DecisionState.DRAFT.value] = (
            first_transition.timestamp - self.created_at
        ).total_seconds()
        
        # Time in intermediate states
        for i in range(len(self.state_history) - 1):
            current_transition = self.state_history[i]
            next_transition = self.state_history[i + 1]
            state = current_transition.to_state.value
            duration = (next_transition.timestamp - current_transition.timestamp).total_seconds()
            durations[state] = durations.get(state, 0) + duration
        
        # Time in current state
        last_transition = self.state_history[-1]
        current_state = last_transition.to_state.value
        end_time = self.finalized_at or datetime.utcnow()
        duration = (end_time - last_transition.timestamp).total_seconds()
        durations[current_state] = durations.get(current_state, 0) + duration
        
        return durations
    
    def get_transition_count(self) -> int:
        """Get number of state transitions"""
        return len(self.state_history)
    
    def has_been_escalated(self) -> bool:
        """Check if decision was ever escalated"""
        return any(
            transition.to_state == DecisionState.ESCALATED
            for transition in self.state_history
        )
    
    def has_been_overridden(self) -> bool:
        """Check if decision was ever overridden"""
        return any(
            transition.to_state == DecisionState.OVERRIDDEN
            for transition in self.state_history
        )
    
    def to_audit_log(self) -> Dict[str, Any]:
        """Convert lifecycle to audit log format"""
        return {
            "decision_id": self.decision_id,
            "current_state": self.current_state.value,
            "is_terminal": self.is_terminal(),
            "is_blocking_automation": self.is_blocking_automation(),
            "created_at": self.created_at.isoformat(),
            "finalized_at": self.finalized_at.isoformat() if self.finalized_at else None,
            "total_lifecycle_time_seconds": self.get_total_lifecycle_time(),
            "transition_count": self.get_transition_count(),
            "has_been_escalated": self.has_been_escalated(),
            "has_been_overridden": self.has_been_overridden(),
            "state_durations": self.get_state_durations(),
            "state_history": [
                {
                    "from_state": t.from_state.value,
                    "to_state": t.to_state.value,
                    "timestamp": t.timestamp.isoformat(),
                    "triggered_by": t.triggered_by,
                    "reason": t.reason
                }
                for t in self.state_history
            ]
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "fnol-2026-01-20-abc123",
                "current_state": "requires_human",
                "state_history": [
                    {
                        "from_state": "draft",
                        "to_state": "evaluated",
                        "triggered_by": "system",
                        "reason": "Decision evaluation completed"
                    },
                    {
                        "from_state": "evaluated",
                        "to_state": "requires_human",
                        "triggered_by": "system",
                        "reason": "Claim amount exceeds monetary boundary"
                    }
                ]
            }
        }


# Helper functions for common lifecycle operations

def create_lifecycle(decision_id: str) -> DecisionLifecycle:
    """Create a new decision lifecycle in DRAFT state"""
    return DecisionLifecycle(decision_id=decision_id)


def evaluate_decision(lifecycle: DecisionLifecycle, triggered_by: str = "system") -> None:
    """Transition from DRAFT to EVALUATED"""
    lifecycle.transition_to(
        new_state=DecisionState.EVALUATED,
        triggered_by=triggered_by,
        reason="Decision evaluation completed"
    )


def require_human_review(
    lifecycle: DecisionLifecycle,
    reason: str,
    triggered_by: str = "system",
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Transition to REQUIRES_HUMAN state"""
    lifecycle.transition_to(
        new_state=DecisionState.REQUIRES_HUMAN,
        triggered_by=triggered_by,
        reason=reason,
        metadata=metadata
    )


def approve_decision(
    lifecycle: DecisionLifecycle,
    actor_id: str,
    reason: str = "Decision approved"
) -> None:
    """Transition to APPROVED state"""
    lifecycle.transition_to(
        new_state=DecisionState.APPROVED,
        triggered_by=actor_id,
        reason=reason
    )


def reject_decision(
    lifecycle: DecisionLifecycle,
    actor_id: str,
    reason: str
) -> None:
    """Transition to REJECTED state"""
    lifecycle.transition_to(
        new_state=DecisionState.REJECTED,
        triggered_by=actor_id,
        reason=reason
    )


def override_decision(
    lifecycle: DecisionLifecycle,
    actor_id: str,
    reason: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Transition to OVERRIDDEN state"""
    lifecycle.transition_to(
        new_state=DecisionState.OVERRIDDEN,
        triggered_by=actor_id,
        reason=reason,
        metadata=metadata
    )


def escalate_decision(
    lifecycle: DecisionLifecycle,
    actor_id: str,
    reason: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Transition to ESCALATED state"""
    lifecycle.transition_to(
        new_state=DecisionState.ESCALATED,
        triggered_by=actor_id,
        reason=reason,
        metadata=metadata
    )


def finalize_decision(
    lifecycle: DecisionLifecycle,
    triggered_by: str,
    reason: str = "Decision finalized"
) -> None:
    """Transition to FINALIZED state"""
    if not lifecycle.can_be_finalized():
        raise ValueError(
            f"Cannot finalize decision in state {lifecycle.current_state.value}. "
            f"Decision must be in APPROVED, REJECTED, or EVALUATED state."
        )
    
    lifecycle.transition_to(
        new_state=DecisionState.FINALIZED,
        triggered_by=triggered_by,
        reason=reason
    )
