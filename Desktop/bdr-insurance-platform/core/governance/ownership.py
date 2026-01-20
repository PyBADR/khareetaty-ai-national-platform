"""Ownership Model - Immutable Ownership Primitives.

Defines who owns decisions, who can override, and who is accountable.
All ownership primitives are immutable (frozen dataclasses).

Rules:
- No anonymous owners
- No shared ownership ambiguity
- One ultimate accountable entity always required
"""

from dataclasses import dataclass
from typing import Literal
from datetime import datetime


@dataclass(frozen=True)
class DecisionOwner:
    """Immutable ownership primitive for a decision.
    
    Attributes:
        owner_id: Unique identifier for the owner (e.g., employee_id, system_id)
        owner_type: Type of owner (human, system, committee)
        organization: Organization unit (e.g., "gig_takaful_kuwait")
        role: Role of the owner (e.g., "claims_manager", "fraud_investigator")
    
    Raises:
        ValueError: If owner_id is empty or anonymous
    """
    
    owner_id: str
    owner_type: Literal["human", "system", "committee"]
    organization: str
    role: str
    
    def __post_init__(self):
        """Validate ownership - no anonymous owners allowed."""
        if not self.owner_id or self.owner_id.strip() == "":
            raise ValueError("owner_id cannot be empty - anonymous owners are forbidden")
        
        if self.owner_id.lower() in ["anonymous", "unknown", "system", "auto"]:
            raise ValueError(
                f"owner_id '{self.owner_id}' is too generic - "
                "must be a specific, identifiable owner"
            )
        
        if not self.organization or self.organization.strip() == "":
            raise ValueError("organization cannot be empty")
        
        if not self.role or self.role.strip() == "":
            raise ValueError("role cannot be empty")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for audit logging."""
        return {
            "owner_id": self.owner_id,
            "owner_type": self.owner_type,
            "organization": self.organization,
            "role": self.role,
        }
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.role}@{self.organization} ({self.owner_type}: {self.owner_id})"


@dataclass(frozen=True)
class AccountabilityChain:
    """Immutable accountability chain for a decision.
    
    Defines the complete ownership hierarchy:
    - primary_owner: Who makes the decision
    - escalation_owner: Who to escalate to if issues arise
    - ultimate_accountable: Who is ultimately responsible (legal/regulatory)
    
    Attributes:
        primary_owner: The primary decision maker
        escalation_owner: The escalation authority
        ultimate_accountable: The ultimate accountable entity
        override_authority: Who can override this decision ("human_only", "system_allowed", "committee_required")
        liability_scope: Scope of liability ("advisory", "financial_decision_support", "automated_action")
        created_at: When this accountability chain was created
    
    Raises:
        ValueError: If ownership chain is ambiguous or invalid
    """
    
    primary_owner: DecisionOwner
    escalation_owner: DecisionOwner
    ultimate_accountable: DecisionOwner
    override_authority: Literal["human_only", "system_allowed", "committee_required"]
    liability_scope: Literal["advisory", "financial_decision_support", "automated_action"]
    created_at: datetime = None
    
    def __post_init__(self):
        """Validate accountability chain - no ambiguity allowed."""
        # Set created_at if not provided (using object.__setattr__ for frozen dataclass)
        if self.created_at is None:
            object.__setattr__(self, 'created_at', datetime.utcnow())
        
        # Validate that all owners are distinct (no self-escalation)
        if self.primary_owner.owner_id == self.escalation_owner.owner_id:
            raise ValueError(
                "primary_owner and escalation_owner cannot be the same - "
                "escalation chain must be distinct"
            )
        
        # Validate that ultimate accountable is at organization level
        if self.ultimate_accountable.owner_type not in ["committee", "human"]:
            raise ValueError(
                "ultimate_accountable must be a human or committee, not a system"
            )
        
        # Validate liability scope matches override authority
        if self.liability_scope == "automated_action" and self.override_authority == "system_allowed":
            raise ValueError(
                "automated_action liability requires human_only or committee_required override"
            )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for audit logging."""
        return {
            "primary_owner": self.primary_owner.to_dict(),
            "escalation_owner": self.escalation_owner.to_dict(),
            "ultimate_accountable": self.ultimate_accountable.to_dict(),
            "override_authority": self.override_authority,
            "liability_scope": self.liability_scope,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def get_audit_summary(self) -> dict:
        """Get a summary for audit records."""
        return {
            "decision_owner": self.primary_owner.owner_id,
            "decision_owner_role": self.primary_owner.role,
            "ultimate_accountable": self.ultimate_accountable.owner_id,
            "ultimate_accountable_org": self.ultimate_accountable.organization,
            "override_authority": self.override_authority,
            "liability_scope": self.liability_scope,
        }
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"Primary: {self.primary_owner} | "
            f"Escalation: {self.escalation_owner} | "
            f"Ultimate: {self.ultimate_accountable}"
        )


def create_system_ownership(
    system_id: str,
    organization: str,
    human_supervisor_id: str,
    human_supervisor_role: str,
    ultimate_accountable_id: str,
    ultimate_accountable_role: str,
) -> AccountabilityChain:
    """Create an accountability chain for system-initiated decisions.
    
    Args:
        system_id: Unique system identifier (e.g., "fnol_triage_engine_v2")
        organization: Organization unit
        human_supervisor_id: ID of human supervisor who oversees the system
        human_supervisor_role: Role of the supervisor
        ultimate_accountable_id: ID of ultimate accountable entity
        ultimate_accountable_role: Role of ultimate accountable
    
    Returns:
        AccountabilityChain with system as primary, human as escalation/ultimate
    """
    primary = DecisionOwner(
        owner_id=system_id,
        owner_type="system",
        organization=organization,
        role="automated_decision_system",
    )
    
    escalation = DecisionOwner(
        owner_id=human_supervisor_id,
        owner_type="human",
        organization=organization,
        role=human_supervisor_role,
    )
    
    ultimate = DecisionOwner(
        owner_id=ultimate_accountable_id,
        owner_type="human",
        organization=organization,
        role=ultimate_accountable_role,
    )
    
    return AccountabilityChain(
        primary_owner=primary,
        escalation_owner=escalation,
        ultimate_accountable=ultimate,
        override_authority="human_only",
        liability_scope="financial_decision_support",
    )


def create_simple_owner(
    owner_id: str,
    organization: str,
    role: str,
    owner_type: str = "human"
) -> DecisionOwner:
    """Create a simple DecisionOwner for testing.
    
    Args:
        owner_id: Unique identifier
        organization: Organization unit
        role: Role of the owner
        owner_type: Type of owner (default: human)
    
    Returns:
        DecisionOwner instance
    """
    return DecisionOwner(
        owner_id=owner_id,
        owner_type=owner_type,
        organization=organization,
        role=role,
    )


def create_human_ownership(
    human_id: str,
    role: str,
    organization: str,
    supervisor_id: str,
    supervisor_role: str,
    ultimate_accountable_id: str,
    ultimate_accountable_role: str,
) -> AccountabilityChain:
    """Create an accountability chain for human-initiated decisions.
    
    Args:
        human_id: Unique human identifier
        role: Role of the decision maker
        organization: Organization unit
        supervisor_id: ID of supervisor
        supervisor_role: Role of supervisor
        ultimate_accountable_id: ID of ultimate accountable entity
        ultimate_accountable_role: Role of ultimate accountable
    
    Returns:
        AccountabilityChain with human as primary
    """
    primary = DecisionOwner(
        owner_id=human_id,
        owner_type="human",
        organization=organization,
        role=role,
    )
    
    escalation = DecisionOwner(
        owner_id=supervisor_id,
        owner_type="human",
        organization=organization,
        role=supervisor_role,
    )
    
    ultimate = DecisionOwner(
        owner_id=ultimate_accountable_id,
        owner_type="human",
        organization=organization,
        role=ultimate_accountable_role,
    )
    
    return AccountabilityChain(
        primary_owner=primary,
        escalation_owner=escalation,
        ultimate_accountable=ultimate,
        override_authority="human_only",
        liability_scope="advisory",
    )
