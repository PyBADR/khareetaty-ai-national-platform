"""Runtime Enforcement - Hard enforcement of ownership and accountability.

This module provides runtime enforcement hooks that MUST be called
before any decision is executed. Violations result in hard failures.

No warnings. No bypasses. No shortcuts.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from core.decision_engine.contract import DecisionRequest
from .ownership import AccountabilityChain
from .accountability import AccountabilityScope, ImpactLevel


class OwnershipViolation(Exception):
    """Raised when ownership requirements are violated.
    
    This is a BLOCKING exception - decisions cannot proceed without ownership.
    """
    pass


class AccountabilityViolation(Exception):
    """Raised when accountability scope is violated.
    
    This is a BLOCKING exception - decisions cannot exceed their scope.
    """
    pass


class AuthorityViolation(Exception):
    """Raised when authority requirements are violated.
    
    This is a BLOCKING exception - decisions cannot proceed without proper authority.
    """
    pass


def enforce_ownership(
    decision_request: DecisionRequest,
    ownership: Optional[AccountabilityChain],
    scope: Optional[AccountabilityScope],
) -> None:
    """Enforce ownership and accountability requirements.
    
    This function MUST be called before:
    - DecisionRequest validation
    - Model inference
    - DecisionResponse creation
    
    Args:
        decision_request: The decision request being processed
        ownership: The accountability chain (REQUIRED)
        scope: The accountability scope (REQUIRED)
    
    Raises:
        OwnershipViolation: If ownership is missing or invalid
        AccountabilityViolation: If decision exceeds scope or attempts forbidden action
    """
    # RULE 1: Ownership is MANDATORY
    if ownership is None:
        raise OwnershipViolation(
            f"Decision {decision_request.decision_id} has no ownership. "
            "All decisions MUST have an AccountabilityChain. "
            "Anonymous decisions are forbidden."
        )
    
    # RULE 2: Accountability scope is MANDATORY
    if scope is None:
        raise AccountabilityViolation(
            f"Decision {decision_request.decision_id} has no accountability scope. "
            "All decisions MUST define their accountability scope."
        )
    
    # RULE 3: Decision type must match scope
    if decision_request.decision_type != scope.decision_type:
        raise AccountabilityViolation(
            f"Decision type mismatch: request has {decision_request.decision_type.value}, "
            f"but scope is for {scope.decision_type.value}"
        )
    
    # RULE 4: Validate financial exposure if present in input_data
    if "claim_amount" in decision_request.input_data:
        amount = float(decision_request.input_data["claim_amount"])
        is_valid, reason = scope.validate_financial_exposure(amount)
        if not is_valid:
            raise AccountabilityViolation(
                f"Financial exposure violation for decision {decision_request.decision_id}: {reason}"
            )
    
    # RULE 5: Validate requested actions against scope
    if "requested_action" in decision_request.input_data:
        action = decision_request.input_data["requested_action"]
        if not scope.is_action_allowed(action):
            if action in scope.forbidden_actions:
                raise AccountabilityViolation(
                    f"Forbidden action '{action}' attempted in decision {decision_request.decision_id}. "
                    f"This action is explicitly forbidden for {scope.decision_type.value} decisions."
                )
            else:
                raise AccountabilityViolation(
                    f"Action '{action}' not allowed in decision {decision_request.decision_id}. "
                    f"Allowed actions: {scope.allowed_actions}"
                )
    
    # RULE 6: Validate override authority if override requested
    if decision_request.override_boundaries:
        if ownership.override_authority == "human_only":
            if ownership.primary_owner.owner_type != "human":
                raise AccountabilityViolation(
                    f"Boundary override requires human authority, "
                    f"but primary owner is {ownership.primary_owner.owner_type}"
                )
        elif ownership.override_authority == "committee_required":
            if ownership.primary_owner.owner_type != "committee":
                raise AccountabilityViolation(
                    f"Boundary override requires committee authority, "
                    f"but primary owner is {ownership.primary_owner.owner_type}"
                )


def validate_ownership_chain(ownership: AccountabilityChain) -> None:
    """Validate that an ownership chain is complete and valid.
    
    Args:
        ownership: The accountability chain to validate
    
    Raises:
        OwnershipViolation: If ownership chain is invalid
    """
    # Validation is already done in AccountabilityChain.__post_init__
    # This function exists for explicit validation calls
    
    # Additional runtime checks
    if ownership.created_at is None:
        raise OwnershipViolation("Ownership chain must have a creation timestamp")
    
    # Check that ownership is not stale (older than 1 year)
    age_days = (datetime.utcnow() - ownership.created_at).days
    if age_days > 365:
        raise OwnershipViolation(
            f"Ownership chain is stale ({age_days} days old). "
            "Ownership must be refreshed annually."
        )


def get_enforcement_metadata(
    ownership: AccountabilityChain,
    scope: AccountabilityScope,
) -> Dict[str, Any]:
    """Get enforcement metadata for audit logging.
    
    Args:
        ownership: The accountability chain
        scope: The accountability scope
    
    Returns:
        Dictionary with enforcement metadata
    """
    return {
        "ownership_enforced": True,
        "enforcement_timestamp": datetime.utcnow().isoformat(),
        "primary_owner": ownership.primary_owner.owner_id,
        "primary_owner_type": ownership.primary_owner.owner_type,
        "ultimate_accountable": ownership.ultimate_accountable.owner_id,
        "override_authority": ownership.override_authority,
        "liability_scope": ownership.liability_scope,
        "max_impact_level": scope.max_impact_level.value,
        "max_financial_exposure": scope.max_financial_exposure,
        "regulatory_class": scope.regulatory_class.value,
        "requires_dual_approval": scope.requires_dual_approval,
    }


def check_action_allowed(
    action: str,
    scope: AccountabilityScope,
    raise_on_forbidden: bool = True,
) -> bool:
    """Check if an action is allowed within the accountability scope.
    
    Args:
        action: The action to check
        scope: The accountability scope
        raise_on_forbidden: If True, raise exception on forbidden action
    
    Returns:
        True if action is allowed
    
    Raises:
        AccountabilityViolation: If action is forbidden and raise_on_forbidden=True
    """
    if action in scope.forbidden_actions:
        if raise_on_forbidden:
            raise AccountabilityViolation(
                f"Action '{action}' is explicitly forbidden for {scope.decision_type.value} decisions"
            )
        return False
    
    if action not in scope.allowed_actions:
        if raise_on_forbidden:
            raise AccountabilityViolation(
                f"Action '{action}' is not in allowed actions: {scope.allowed_actions}"
            )
        return False
    
    return True


def enforce_authority(
    decision_request: DecisionRequest,
    authority: "DecisionAuthority",
    ownership: AccountabilityChain,
    scope: AccountabilityScope,
) -> None:
    """Enforce authority requirements before decision execution.
    
    This function MUST be called AFTER boundary evaluation and BEFORE decision execution.
    
    Enforcement flow:
    1. DecisionRequest
    2. Boundary Evaluation
    3. Authority Resolution
    4. Authority Enforcement (THIS FUNCTION)
    5. Human-in-the-loop (if required)
    6. Decision Execution
    
    Args:
        decision_request: The decision request being processed
        authority: The resolved decision authority
        ownership: The accountability chain
        scope: The accountability scope
    
    Raises:
        AuthorityViolation: If authority requirements are violated
    """
    from .authority import DecisionSeverity, calculate_decision_severity
    
    # RULE 1: Authority cannot execute
    if not authority.can_execute:
        raise AuthorityViolation(
            f"Execution not permitted for authority '{authority.authority_id}' (role: {authority.role}). "
            f"This authority does not have execute permission."
        )
    
    # RULE 2: Severity exceeds authority limit
    severity = calculate_decision_severity(decision_request, scope.max_impact_level)
    if not authority.can_handle_severity(severity):
        raise AuthorityViolation(
            f"Severity {severity.name} exceeds authority limit {authority.max_decision_severity.name} "
            f"for role '{authority.role}'. Escalation required."
        )
    
    # RULE 3: Override requested without override rights
    if decision_request.override_boundaries and not authority.can_override:
        raise AuthorityViolation(
            f"Override requested but authority '{authority.authority_id}' (role: {authority.role}) "
            f"does not have override permission. Override requires elevated authority."
        )
    
    # RULE 4: Finalization attempted without authority
    if decision_request.metadata.get("finalize", False) and not authority.can_finalize:
        raise AuthorityViolation(
            f"Finalization attempted but authority '{authority.authority_id}' (role: {authority.role}) "
            f"does not have finalize permission. Finalization requires elevated authority."
        )
    
    # RULE 5: Human signature required but missing
    if authority.requires_human_signature:
        if not decision_request.metadata.get("human_signature"):
            raise AuthorityViolation(
                f"Human signature required for authority '{authority.authority_id}' (role: {authority.role}) "
                f"but no signature provided. Decision cannot proceed without human approval."
            )
    
    # RULE 6: Committee approval required but missing
    if authority.requires_committee:
        if not decision_request.metadata.get("committee_approval"):
            raise AuthorityViolation(
                f"Committee approval required for authority '{authority.authority_id}' (role: {authority.role}) "
                f"but no committee approval provided. Decision cannot proceed without committee review."
            )
    
    # RULE 7: Decision type not allowed
    if not authority.can_handle_decision_type(decision_request.decision_type):
        raise AuthorityViolation(
            f"Decision type {decision_request.decision_type.value} not allowed for authority "
            f"'{authority.authority_id}' (role: {authority.role}). "
            f"Allowed types: {[dt.value for dt in authority.allowed_decision_types]}"
        )


def get_authority_metadata(
    authority: "DecisionAuthority",
) -> Dict[str, Any]:
    """Get authority metadata for audit logging.
    
    Args:
        authority: The decision authority
    
    Returns:
        Dictionary with authority metadata
    """
    return {
        "authority_id": authority.authority_id,
        "authority_role": authority.role,
        "authority_checks_passed": True,
        "authority_enforcement_timestamp": datetime.utcnow().isoformat(),
        "can_execute": authority.can_execute,
        "can_override": authority.can_override,
        "can_finalize": authority.can_finalize,
        "requires_human_signature": authority.requires_human_signature,
        "requires_committee": authority.requires_committee,
        "max_decision_severity": authority.max_decision_severity.name,
        "allowed_decision_types": [dt.value for dt in authority.allowed_decision_types],
    }


# ============================================================================
# Authority Anchor Enforcement (Phase 2.2)
# ============================================================================

class AuthorityAnchorViolation(Exception):
    """Raised when authority anchor requirements are violated.
    
    This is a BLOCKING exception in production - decisions cannot proceed
    without a valid, legally attributable authority anchor.
    """
    pass


def enforce_authority_anchor(
    authority: Any,  # DecisionAuthority with anchor
    environment: str = "production",
    required_jurisdiction: Optional[Any] = None  # Optional[Jurisdiction]
) -> None:
    """Enforce authority anchor requirements.
    
    This function MUST be called in production before decision execution.
    It ensures every decision is legally attributable to a specific human
    authority under a specific jurisdiction and mandate.
    
    PRODUCTION RULES (NON-BYPASSABLE):
    1. Authority must have a valid anchor
    2. Anchor must be currently valid (time window)
    3. Anchor must match required jurisdiction (if specified)
    4. Anchor must have contract reference
    
    Args:
        authority: Decision authority (must have authority_anchor attribute)
        environment: Current environment (dev, staging, production)
        required_jurisdiction: Required jurisdiction (or None for any)
    
    Raises:
        AuthorityAnchorViolation: If anchor requirements are violated in production
    """
    from .authority_anchor import validate_anchor_for_production
    
    # Check if we're in production
    is_production = environment.lower() in ("production", "prod")
    
    # Get anchor from authority
    anchor = getattr(authority, "authority_anchor", None)
    
    # In production, anchor is MANDATORY
    if is_production:
        if anchor is None:
            raise AuthorityAnchorViolation(
                "PRODUCTION BLOCK: No authority anchor provided. "
                "All production decisions must be legally attributable to a specific "
                "human authority under a specific jurisdiction and mandate. "
                "This is a non-bypassable requirement."
            )
        
        # Validate anchor for production use
        is_valid, error_message = validate_anchor_for_production(anchor, required_jurisdiction)
        
        if not is_valid:
            raise AuthorityAnchorViolation(
                f"PRODUCTION BLOCK: Authority anchor validation failed. {error_message}"
            )
    
    # In non-production, log warning but don't block
    else:
        if anchor is None:
            # Log warning (in production system, this would go to logging)
            import warnings
            warnings.warn(
                f"[{environment.upper()}] No authority anchor provided. "
                "This would block execution in production.",
                UserWarning
            )


def get_anchor_audit_metadata(authority: Any) -> Dict[str, Any]:
    """Get authority anchor metadata for audit logging.
    
    Args:
        authority: Decision authority with anchor
    
    Returns:
        Dictionary with anchor metadata for audit trail
    """
    anchor = getattr(authority, "authority_anchor", None)
    
    if anchor is None:
        return {
            "has_anchor": False,
            "anchor_warning": "No authority anchor - would block in production"
        }
    
    return {
        "has_anchor": True,
        "anchor_id": anchor.anchor_id,
        "legal_entity": anchor.legal_entity,
        "jurisdiction": anchor.jurisdiction.value,
        "job_title": anchor.job_title,
        "contract_reference": anchor.contract_reference,
        "valid_from": anchor.valid_from.isoformat(),
        "valid_until": anchor.valid_until.isoformat() if anchor.valid_until else None,
        "is_currently_valid": anchor.is_currently_valid(),
        "days_until_expiry": anchor.days_until_expiry(),
    }


def create_enforcement_explanation(
    allowed: bool,
    reason: str,
    anchor: Optional[Any] = None,
    environment: str = "production"
) -> Any:  # AuthorityExplanation
    """Create an authority explanation for enforcement decision.
    
    Args:
        allowed: Whether decision was allowed
        reason: Reason for allowing or blocking
        anchor: Authority anchor (if available)
        environment: Current environment
    
    Returns:
        AuthorityExplanation instance
    """
    from .authority_anchor import create_authority_explanation
    
    governing_policy = (
        "Production Authority Anchor Policy - Phase 2.2" if environment.lower() in ("production", "prod")
        else f"{environment.title()} Environment Policy"
    )
    
    return create_authority_explanation(
        allowed=allowed,
        reason=reason,
        governing_policy=governing_policy,
        anchor=anchor
    )
