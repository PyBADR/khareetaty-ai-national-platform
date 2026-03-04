"""
Decision Engine - Core Platform Service

Orchestrates decision workflows and manages decision lifecycle.

Key Components:
- DecisionOrchestrator: Main entry point for all decisions
- DecisionType: ADVISORY, BOUNDED, SIMULATION
- DecisionContext: User, timestamp, trace_id, etc.
- DecisionResult: Outcome, confidence, reasoning

Contract Components (Formal Decision Contract):
- DecisionRequest: Standard request format
- DecisionResponse: ONLY valid return type (raw dicts forbidden)
- AuditMetadata: Mandatory audit trail
- BoundaryResult: Boundary enforcement
- Explainability: Mandatory explainability

Governance Components (Phase 2 - Decision Governance Runtime):
- DecisionPosition: Ownership & liability contract
- HumanDecisionAction: Signed human actions
- DecisionLifecycle: State machine for decision flow
- GovernanceEnforcer: Runtime enforcement (BLOCKS on violations)

Version: 2.1.0 (Governance Runtime)
"""

# Legacy components (maintained for backward compatibility)
from .orchestrator import DecisionOrchestrator
from .models import DecisionType, DecisionContext, DecisionResult, Decision

# Formal Decision Contract (Contract-First)
from .contract import DecisionRequest, DecisionResponse, AuditMetadata
from .boundaries import BoundaryResult, BoundaryCheck, BoundaryType, create_boundary_result
from .explainability import Explainability, DecisionFactor, ScoredSignal, Evidence
from .enums import DecisionType as DecisionTypeEnum

# Governance Runtime (Phase 2)
from .position import (
    DecisionPosition,
    DecisionDomain,
    RiskClass,
    LiabilityScope,
    EscalationPolicy,
    OverrideAuthority,
    RegulatoryContext,
    create_claims_position,
    create_underwriting_position,
    create_fraud_position,
)
from .human_action import (
    HumanDecisionAction,
    HumanActionType,
    RejectionReasonCode,
    OverrideJustificationType,
    HumanActionChain,
    create_approval_action,
    create_rejection_action,
    create_override_action,
)
from .lifecycle import (
    DecisionLifecycle,
    DecisionState,
    StateTransition,
    create_lifecycle,
    evaluate_decision,
    require_human_review,
    approve_decision,
    reject_decision,
    override_decision,
    escalate_decision,
    finalize_decision,
)
from .enforcement import (
    GovernanceEnforcer,
    EnforcementResult,
    EnforcementViolation,
    GovernanceViolationError,
    enforce_strict,
    enforce_permissive,
    check_compliance,
)

__all__ = [
    # Legacy components
    "DecisionOrchestrator",
    "DecisionType",
    "DecisionContext",
    "DecisionResult",
    "Decision",
    # Contract components
    "DecisionRequest",
    "DecisionResponse",
    "AuditMetadata",
    "BoundaryResult",
    "BoundaryCheck",
    "BoundaryType",
    "create_boundary_result",
    "Explainability",
    "DecisionFactor",
    "ScoredSignal",
    "Evidence",
    "DecisionTypeEnum",
    # Governance components (Phase 2)
    "DecisionPosition",
    "DecisionDomain",
    "RiskClass",
    "LiabilityScope",
    "EscalationPolicy",
    "OverrideAuthority",
    "RegulatoryContext",
    "create_claims_position",
    "create_underwriting_position",
    "create_fraud_position",
    "HumanDecisionAction",
    "HumanActionType",
    "RejectionReasonCode",
    "OverrideJustificationType",
    "HumanActionChain",
    "create_approval_action",
    "create_rejection_action",
    "create_override_action",
    "DecisionLifecycle",
    "DecisionState",
    "StateTransition",
    "create_lifecycle",
    "evaluate_decision",
    "require_human_review",
    "approve_decision",
    "reject_decision",
    "override_decision",
    "escalate_decision",
    "finalize_decision",
    "GovernanceEnforcer",
    "EnforcementResult",
    "EnforcementViolation",
    "GovernanceViolationError",
    "enforce_strict",
    "enforce_permissive",
    "check_compliance",
]
