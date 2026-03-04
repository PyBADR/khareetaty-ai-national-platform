"""
Governance Module

Provides human-in-the-loop controls, validation, and compliance enforcement
for all decision-making processes.
"""

from .validators import InputValidator, JustificationValidator
from .human_oversight import HumanOversightManager, OversightLevel
from .compliance import ComplianceChecker, ComplianceRule

# Phase 2.1: Ownership & Accountability Layer
from .ownership import (
    DecisionOwner,
    AccountabilityChain,
    create_system_ownership,
    create_human_ownership,
    create_simple_owner,
)

from .accountability import (
    AccountabilityScope,
    ImpactLevel,
    RegulatoryClass,
    ADVISORY_SCOPE,
    BOUNDED_LOW_SCOPE,
    BOUNDED_MEDIUM_SCOPE,
    BOUNDED_HIGH_SCOPE,
    SIMULATION_SCOPE,
    get_scope_for_decision_type,
)

from .enforcement import (
    OwnershipViolation,
    AccountabilityViolation,
    AuthorityViolation,
    enforce_ownership,
    enforce_authority,
    validate_ownership_chain,
    get_enforcement_metadata,
    get_authority_metadata,
    check_action_allowed,
)

# Phase 2.1.1: Decision Authority Layer
from .authority import (
    DecisionAuthority,
    DecisionSeverity,
    OwnershipContext,
    resolve_decision_authority,
    calculate_decision_severity,
)

from .validators import (
    validate_authority_in_response,
    validate_authority_severity_match,
    validate_no_authority_bypass,
    validate_human_required_authority,
)

# Phase 2.2: Authority Anchor + Production Gate
from .authority_anchor import (
    AuthorityAnchor,
    Jurisdiction,
    AuthorityExplanation,
    create_authority_anchor,
    validate_anchor_for_production,
    create_authority_explanation,
)

from .enforcement import (
    AuthorityAnchorViolation,
    enforce_authority_anchor,
    get_anchor_audit_metadata,
    create_enforcement_explanation,
)

__all__ = [
    'InputValidator',
    'JustificationValidator',
    'HumanOversightManager',
    'OversightLevel',
    'ComplianceChecker',
    'ComplianceRule',
    # Phase 2.1: Ownership & Accountability
    'DecisionOwner',
    'AccountabilityChain',
    'create_system_ownership',
    'create_human_ownership',
    'create_simple_owner',
    'AccountabilityScope',
    'ImpactLevel',
    'RegulatoryClass',
    'ADVISORY_SCOPE',
    'BOUNDED_LOW_SCOPE',
    'BOUNDED_MEDIUM_SCOPE',
    'BOUNDED_HIGH_SCOPE',
    'SIMULATION_SCOPE',
    'get_scope_for_decision_type',
    'OwnershipViolation',
    'AccountabilityViolation',
    'AuthorityViolation',
    'enforce_ownership',
    'enforce_authority',
    'validate_ownership_chain',
    'get_enforcement_metadata',
    'get_authority_metadata',
    'check_action_allowed',
    # Phase 2.1.1: Decision Authority
    'DecisionAuthority',
    'DecisionSeverity',
    'OwnershipContext',
    'resolve_decision_authority',
    'calculate_decision_severity',
    'validate_authority_in_response',
    'validate_authority_severity_match',
    'validate_no_authority_bypass',
    'validate_human_required_authority',
    # Phase 2.2: Authority Anchor + Production Gate
    'AuthorityAnchor',
    'Jurisdiction',
    'AuthorityExplanation',
    'create_authority_anchor',
    'validate_anchor_for_production',
    'create_authority_explanation',
    'AuthorityAnchorViolation',
    'enforce_authority_anchor',
    'get_anchor_audit_metadata',
    'create_enforcement_explanation',
]
