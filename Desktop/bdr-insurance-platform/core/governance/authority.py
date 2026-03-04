"""Decision Authority Layer - Executable, Enforced, Auditable.

Defines WHO is allowed to execute, override, or finalize a decision.

Key Concept: Ownership ≠ Authority
- Ownership: Who is responsible for the decision
- Authority: Who has permission to execute/override/finalize

This module provides:
- Immutable authority primitives
- Authority resolution logic
- Integration with ownership and accountability
"""

from dataclasses import dataclass
from typing import Set, Optional, Any
from enum import Enum

from core.decision_engine.enums import DecisionType
from core.decision_engine.contract import DecisionRequest
from .ownership import AccountabilityChain, DecisionOwner
from .accountability import ImpactLevel


class DecisionSeverity(int, Enum):
    """Decision severity classification.
    
    Severity determines required authority level:
    1 = ROUTINE: Standard operations, minimal risk
    2 = ELEVATED: Requires senior approval
    3 = CRITICAL: Requires executive approval
    4 = EMERGENCY: Requires committee approval
    5 = CATASTROPHIC: Requires board approval
    """
    ROUTINE = 1
    ELEVATED = 2
    CRITICAL = 3
    EMERGENCY = 4
    CATASTROPHIC = 5


@dataclass(frozen=True)
class DecisionAuthority:
    """Immutable authority primitive defining execution permissions.
    
    Attributes:
        authority_id: Unique identifier for this authority grant
        role: Role granted this authority (e.g., "claims_manager", "fraud_investigator")
        can_execute: Permission to execute decisions
        can_override: Permission to override boundary violations
        can_finalize: Permission to finalize decisions (make them binding)
        requires_human_signature: Whether human signature is required
        requires_committee: Whether committee approval is required
        max_decision_severity: Maximum severity level this authority can handle
        allowed_decision_types: Set of decision types this authority can process
        authority_anchor: Legal anchor for this authority (Phase 2.2)
    
    Rules:
        - All fields are required (no defaults)
        - Immutable (frozen=True)
        - No optional fields (except authority_anchor in dev/staging)
        - Authority must be explicitly granted
        - In production, authority_anchor is MANDATORY
    
    Raises:
        ValueError: If authority configuration is invalid
    """
    
    authority_id: str
    role: str
    can_execute: bool
    can_override: bool
    can_finalize: bool
    requires_human_signature: bool
    requires_committee: bool
    max_decision_severity: DecisionSeverity
    allowed_decision_types: Set[DecisionType]
    authority_anchor: Optional[Any] = None  # AuthorityAnchor - MANDATORY in production
    
    def __post_init__(self):
        """Validate authority configuration."""
        # Validate authority_id
        if not self.authority_id or self.authority_id.strip() == "":
            raise ValueError("authority_id cannot be empty")
        
        # Validate role
        if not self.role or self.role.strip() == "":
            raise ValueError("role cannot be empty")
        
        # Validate allowed_decision_types is not empty
        if not self.allowed_decision_types:
            raise ValueError("allowed_decision_types cannot be empty - must specify at least one decision type")
        
        # Validate logical consistency: can't finalize without execute
        if self.can_finalize and not self.can_execute:
            raise ValueError("Cannot have finalize permission without execute permission")
        
        # Validate logical consistency: committee decisions require human signature
        if self.requires_committee and not self.requires_human_signature:
            raise ValueError("Committee approval requires human signature")
        
        # Validate severity level is valid
        if not isinstance(self.max_decision_severity, DecisionSeverity):
            raise ValueError(f"max_decision_severity must be DecisionSeverity enum, got {type(self.max_decision_severity)}")
    
    def can_handle_severity(self, severity: DecisionSeverity) -> bool:
        """Check if this authority can handle the given severity level.
        
        Args:
            severity: The severity level to check
        
        Returns:
            True if this authority can handle the severity, False otherwise
        """
        return severity.value <= self.max_decision_severity.value
    
    def can_handle_decision_type(self, decision_type: DecisionType) -> bool:
        """Check if this authority can handle the given decision type.
        
        Args:
            decision_type: The decision type to check
        
        Returns:
            True if this authority can handle the decision type, False otherwise
        """
        return decision_type in self.allowed_decision_types


class OwnershipContext:
    """Context wrapper for ownership information.
    
    Provides a clean interface for authority resolution.
    """
    
    def __init__(self, ownership: AccountabilityChain):
        """Initialize ownership context.
        
        Args:
            ownership: The accountability chain
        """
        self.ownership = ownership
    
    @property
    def primary_owner(self) -> DecisionOwner:
        """Get the primary owner."""
        return self.ownership.primary_owner
    
    @property
    def escalation_owner(self) -> DecisionOwner:
        """Get the escalation owner."""
        return self.ownership.escalation_owner
    
    @property
    def ultimate_accountable(self) -> DecisionOwner:
        """Get the ultimate accountable party."""
        return self.ownership.ultimate_accountable


def calculate_decision_severity(
    request: DecisionRequest,
    impact_level: ImpactLevel
) -> DecisionSeverity:
    """Calculate decision severity based on request and impact level.
    
    Severity calculation rules:
    - SIMULATION decisions: Always ROUTINE
    - ADVISORY decisions: ROUTINE to ELEVATED based on impact
    - BOUNDED decisions: ROUTINE to CRITICAL based on impact
    - Impact CRITICAL: Always CRITICAL or higher severity
    
    Args:
        request: The decision request
        impact_level: The impact level from accountability scope
    
    Returns:
        The calculated decision severity
    """
    # SIMULATION decisions are always ROUTINE
    if request.decision_type == DecisionType.SIMULATION:
        return DecisionSeverity.ROUTINE
    
    # Map impact level to severity
    if impact_level == ImpactLevel.MINIMAL:
        return DecisionSeverity.ROUTINE
    elif impact_level == ImpactLevel.LOW:
        return DecisionSeverity.ROUTINE if request.decision_type == DecisionType.ADVISORY else DecisionSeverity.ELEVATED
    elif impact_level == ImpactLevel.MEDIUM:
        return DecisionSeverity.ELEVATED
    elif impact_level == ImpactLevel.HIGH:
        return DecisionSeverity.CRITICAL
    elif impact_level == ImpactLevel.CRITICAL:
        return DecisionSeverity.CRITICAL
    else:
        # Default to CRITICAL for unknown impact levels
        return DecisionSeverity.CRITICAL


def resolve_decision_authority(
    request: DecisionRequest,
    ownership: OwnershipContext
) -> DecisionAuthority:
    """Resolve decision authority based on request and ownership.
    
    Authority resolution rules:
    1. Primary owner gets base authority for their role
    2. Escalation owner gets elevated authority
    3. Ultimate accountable gets full authority
    4. Authority level depends on decision type and severity
    
    This function MUST NOT:
    - Use hardcoded shortcuts
    - Guess roles
    - Grant authority without validation
    
    Args:
        request: The decision request
        ownership: The ownership context
    
    Returns:
        The resolved decision authority
    
    Raises:
        ValueError: If authority cannot be resolved
    """
    # Validate inputs
    if not request:
        raise ValueError("request cannot be None")
    if not ownership:
        raise ValueError("ownership cannot be None")
    
    # Get the primary owner's role
    primary_role = ownership.primary_owner.role
    owner_type = ownership.primary_owner.owner_type
    
    # Calculate severity from request metadata
    # Default to ROUTINE if not specified
    severity = DecisionSeverity.ROUTINE
    if hasattr(request, 'accountability_scope') and request.accountability_scope:
        impact_level = request.accountability_scope.max_impact_level
        severity = calculate_decision_severity(request, impact_level)
    
    # Resolve authority based on owner type and role
    if owner_type == "system":
        # System owners have limited authority
        return _resolve_system_authority(
            primary_role=primary_role,
            decision_type=request.decision_type,
            severity=severity
        )
    elif owner_type == "human":
        # Human owners have standard authority
        return _resolve_human_authority(
            primary_role=primary_role,
            decision_type=request.decision_type,
            severity=severity
        )
    elif owner_type == "committee":
        # Committee owners have elevated authority
        return _resolve_committee_authority(
            primary_role=primary_role,
            decision_type=request.decision_type,
            severity=severity
        )
    else:
        raise ValueError(f"Unknown owner_type: {owner_type}")


def _resolve_system_authority(
    primary_role: str,
    decision_type: DecisionType,
    severity: DecisionSeverity
) -> DecisionAuthority:
    """Resolve authority for system owners.
    
    System owners have limited authority:
    - Can execute ROUTINE decisions only
    - Cannot override
    - Cannot finalize
    - No human signature required (system-to-system)
    - No committee required
    """
    # System can only handle ROUTINE severity
    if severity != DecisionSeverity.ROUTINE:
        raise ValueError(f"System authority cannot handle severity {severity.name} - requires human authority")
    
    # System can only handle SIMULATION and BOUNDED decisions
    if decision_type == DecisionType.ADVISORY:
        raise ValueError("System authority cannot handle ADVISORY decisions - requires human authority")
    
    return DecisionAuthority(
        authority_id=f"system_{primary_role}_{decision_type.value}",
        role=primary_role,
        can_execute=True,
        can_override=False,
        can_finalize=False,
        requires_human_signature=False,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ROUTINE,
        allowed_decision_types={DecisionType.SIMULATION, DecisionType.BOUNDED}
    )


def _resolve_human_authority(
    primary_role: str,
    decision_type: DecisionType,
    severity: DecisionSeverity
) -> DecisionAuthority:
    """Resolve authority for human owners.
    
    Human owners have standard authority based on role and severity.
    """
    # Map role to authority level
    role_lower = primary_role.lower()
    
    # Senior roles get elevated authority
    is_senior = any(keyword in role_lower for keyword in [
        "senior", "lead", "manager", "director", "head", "chief"
    ])
    
    # Executive roles get critical authority
    is_executive = any(keyword in role_lower for keyword in [
        "director", "vp", "vice president", "chief", "cto", "cfo", "ceo"
    ])
    
    # Determine max severity based on role
    if is_executive:
        max_severity = DecisionSeverity.CRITICAL
        can_override = True
        can_finalize = True
    elif is_senior:
        max_severity = DecisionSeverity.ELEVATED
        can_override = True
        can_finalize = severity.value <= DecisionSeverity.ELEVATED.value
    else:
        max_severity = DecisionSeverity.ROUTINE
        can_override = False
        can_finalize = severity.value <= DecisionSeverity.ROUTINE.value
    
    # Check if requested severity exceeds authority
    if severity.value > max_severity.value:
        raise ValueError(
            f"Role '{primary_role}' cannot handle severity {severity.name} "
            f"(max: {max_severity.name}) - requires escalation"
        )
    
    # Determine if human signature required
    requires_signature = severity.value >= DecisionSeverity.ELEVATED.value
    
    # Determine allowed decision types
    if decision_type == DecisionType.ADVISORY:
        allowed_types = {DecisionType.ADVISORY, DecisionType.SIMULATION}
    else:
        allowed_types = {DecisionType.ADVISORY, DecisionType.BOUNDED, DecisionType.SIMULATION}
    
    return DecisionAuthority(
        authority_id=f"human_{primary_role}_{decision_type.value}_{severity.name}",
        role=primary_role,
        can_execute=True,
        can_override=can_override,
        can_finalize=can_finalize,
        requires_human_signature=requires_signature,
        requires_committee=False,
        max_decision_severity=max_severity,
        allowed_decision_types=allowed_types
    )


def _resolve_committee_authority(
    primary_role: str,
    decision_type: DecisionType,
    severity: DecisionSeverity
) -> DecisionAuthority:
    """Resolve authority for committee owners.
    
    Committee owners have elevated authority:
    - Can handle up to EMERGENCY severity
    - Can override
    - Can finalize
    - Requires human signature
    - Requires committee approval
    """
    # Committee can handle up to EMERGENCY severity
    if severity == DecisionSeverity.CATASTROPHIC:
        raise ValueError(
            f"Committee authority cannot handle CATASTROPHIC severity - requires board approval"
        )
    
    return DecisionAuthority(
        authority_id=f"committee_{primary_role}_{decision_type.value}_{severity.name}",
        role=primary_role,
        can_execute=True,
        can_override=True,
        can_finalize=True,
        requires_human_signature=True,
        requires_committee=True,
        max_decision_severity=DecisionSeverity.EMERGENCY,
        allowed_decision_types={DecisionType.ADVISORY, DecisionType.BOUNDED, DecisionType.SIMULATION}
    )
