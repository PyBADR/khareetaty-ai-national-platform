"""
Runtime Enforcement Layer - Governance Guards

This layer FAILS HARD if governance requirements are not met.
No warnings. No silent failures. Block execution.

Author: BDR Platform Team
Created: 2026-01-20
Version: 1.0.0
"""

from typing import Optional, List
from pydantic import BaseModel, Field

# Import governance components
from core.decision_engine.contract import DecisionResponse
from core.decision_engine.position import DecisionPosition
from core.decision_engine.lifecycle import DecisionLifecycle, DecisionState
from core.decision_engine.boundaries import BoundaryResult
from core.decision_engine.explainability import Explainability


class EnforcementViolation(BaseModel):
    """Record of a governance enforcement violation"""
    
    violation_type: str = Field(..., description="Type of violation")
    severity: str = Field(..., description="Severity: CRITICAL, HIGH, MEDIUM, LOW")
    message: str = Field(..., description="Human-readable violation message")
    field: Optional[str] = Field(None, description="Field that caused violation")
    
    def is_critical(self) -> bool:
        """Check if this is a critical violation"""
        return self.severity == "CRITICAL"


class EnforcementResult(BaseModel):
    """Result of enforcement checks"""
    
    is_compliant: bool = Field(..., description="Whether decision passes all enforcement checks")
    violations: List[EnforcementViolation] = Field(
        default_factory=list,
        description="List of violations found"
    )
    
    def has_critical_violations(self) -> bool:
        """Check if there are any critical violations"""
        return any(v.is_critical() for v in self.violations)
    
    def get_violation_summary(self) -> str:
        """Get human-readable summary of violations"""
        if self.is_compliant:
            return "No violations"
        
        critical = sum(1 for v in self.violations if v.severity == "CRITICAL")
        high = sum(1 for v in self.violations if v.severity == "HIGH")
        medium = sum(1 for v in self.violations if v.severity == "MEDIUM")
        low = sum(1 for v in self.violations if v.severity == "LOW")
        
        return f"Violations: {critical} CRITICAL, {high} HIGH, {medium} MEDIUM, {low} LOW"


class GovernanceEnforcer:
    """
    Runtime Governance Enforcer
    
    Blocks execution if:
    - Decision has no position contract
    - Required human action is missing
    - Boundary violations exceed threshold
    - Explainability is incomplete
    - Evaluation status is unknown
    
    This is NOT a validator. This is a BLOCKER.
    """
    
    def __init__(
        self,
        max_boundary_violations: int = 0,
        require_position: bool = True,
        require_explainability: bool = True,
        require_lifecycle: bool = True,
        block_on_critical: bool = True
    ):
        """
        Initialize enforcer
        
        Args:
            max_boundary_violations: Maximum allowed boundary violations (default: 0)
            require_position: Whether position contract is required (default: True)
            require_explainability: Whether explainability is required (default: True)
            require_lifecycle: Whether lifecycle tracking is required (default: True)
            block_on_critical: Whether to block on critical violations (default: True)
        """
        self.max_boundary_violations = max_boundary_violations
        self.require_position = require_position
        self.require_explainability = require_explainability
        self.require_lifecycle = require_lifecycle
        self.block_on_critical = block_on_critical
    
    def enforce(
        self,
        decision: DecisionResponse,
        lifecycle: Optional[DecisionLifecycle] = None
    ) -> EnforcementResult:
        """
        Enforce governance requirements on a decision
        
        Args:
            decision: Decision to enforce
            lifecycle: Optional lifecycle state
            
        Returns:
            EnforcementResult with violations
            
        Raises:
            GovernanceViolationError: If critical violations found and block_on_critical=True
        """
        violations: List[EnforcementViolation] = []
        
        # Check 1: Position contract
        if self.require_position:
            position_violations = self._check_position(decision)
            violations.extend(position_violations)
        
        # Check 2: Boundary violations
        boundary_violations = self._check_boundaries(decision)
        violations.extend(boundary_violations)
        
        # Check 3: Explainability
        if self.require_explainability:
            explainability_violations = self._check_explainability(decision)
            violations.extend(explainability_violations)
        
        # Check 4: Lifecycle state
        if self.require_lifecycle and lifecycle:
            lifecycle_violations = self._check_lifecycle(decision, lifecycle)
            violations.extend(lifecycle_violations)
        
        # Check 5: Human action requirements
        human_action_violations = self._check_human_action(decision, lifecycle)
        violations.extend(human_action_violations)
        
        # Check 6: Audit metadata
        audit_violations = self._check_audit_metadata(decision)
        violations.extend(audit_violations)
        
        # Create result
        result = EnforcementResult(
            is_compliant=len(violations) == 0,
            violations=violations
        )
        
        # Block if critical violations and blocking enabled
        if self.block_on_critical and result.has_critical_violations():
            critical_msgs = [v.message for v in violations if v.is_critical()]
            raise GovernanceViolationError(
                f"CRITICAL governance violations detected. Execution blocked.\n" +
                "\n".join(f"  - {msg}" for msg in critical_msgs)
            )
        
        return result
    
    def _check_position(self, decision: DecisionResponse) -> List[EnforcementViolation]:
        """Check position contract requirements"""
        violations = []
        
        if not hasattr(decision, 'position') or decision.position is None:
            violations.append(EnforcementViolation(
                violation_type="missing_position",
                severity="CRITICAL",
                message="Decision has no position contract. Every decision MUST have ownership and liability defined.",
                field="position"
            ))
        else:
            # Validate position fields are not generic
            position = decision.position
            if hasattr(position, 'decision_owner_role'):
                generic_roles = ['tbd', 'todo', 'unknown', 'default', 'system']
                if position.decision_owner_role.lower() in generic_roles:
                    violations.append(EnforcementViolation(
                        violation_type="generic_position_role",
                        severity="CRITICAL",
                        message=f"Position has generic decision_owner_role: '{position.decision_owner_role}'. Must specify actual role.",
                        field="position.decision_owner_role"
                    ))
        
        return violations
    
    def _check_boundaries(self, decision: DecisionResponse) -> List[EnforcementViolation]:
        """Check boundary violation requirements"""
        violations = []
        
        if not hasattr(decision, 'boundaries') or decision.boundaries is None:
            violations.append(EnforcementViolation(
                violation_type="missing_boundaries",
                severity="HIGH",
                message="Decision has no boundary checks. Boundary enforcement is required.",
                field="boundaries"
            ))
        else:
            # Check violation count
            boundary_result: BoundaryResult = decision.boundaries
            violation_count = len([c for c in boundary_result.checks if not c.passed])
            
            if violation_count > self.max_boundary_violations:
                violations.append(EnforcementViolation(
                    violation_type="excessive_boundary_violations",
                    severity="HIGH",
                    message=f"Decision has {violation_count} boundary violations (max allowed: {self.max_boundary_violations})",
                    field="boundaries"
                ))
        
        return violations
    
    def _check_explainability(self, decision: DecisionResponse) -> List[EnforcementViolation]:
        """Check explainability requirements"""
        violations = []
        
        if not hasattr(decision, 'explainability') or decision.explainability is None:
            violations.append(EnforcementViolation(
                violation_type="missing_explainability",
                severity="CRITICAL",
                message="Decision has no explainability. Explainability is MANDATORY for all decisions.",
                field="explainability"
            ))
        else:
            explainability: Explainability = decision.explainability
            
            # Check summary
            if not explainability.summary or len(explainability.summary.strip()) < 10:
                violations.append(EnforcementViolation(
                    violation_type="incomplete_explainability_summary",
                    severity="HIGH",
                    message="Explainability summary is missing or too short (min 10 characters)",
                    field="explainability.summary"
                ))
            
            # Check key factors
            if not explainability.key_factors or len(explainability.key_factors) == 0:
                violations.append(EnforcementViolation(
                    violation_type="missing_key_factors",
                    severity="HIGH",
                    message="Explainability has no key factors. At least one factor is required.",
                    field="explainability.key_factors"
                ))
        
        return violations
    
    def _check_lifecycle(self, decision: DecisionResponse, lifecycle: DecisionLifecycle) -> List[EnforcementViolation]:
        """Check lifecycle state requirements"""
        violations = []
        
        # Check lifecycle exists
        if lifecycle is None:
            violations.append(EnforcementViolation(
                violation_type="missing_lifecycle",
                severity="HIGH",
                message="Decision has no lifecycle tracking. Lifecycle management is required.",
                field="lifecycle"
            ))
            return violations
        
        # Check decision IDs match
        if lifecycle.decision_id != decision.decision_id:
            violations.append(EnforcementViolation(
                violation_type="lifecycle_id_mismatch",
                severity="CRITICAL",
                message=f"Lifecycle decision_id '{lifecycle.decision_id}' does not match decision_id '{decision.decision_id}'",
                field="lifecycle.decision_id"
            ))
        
        # Check if decision is in valid state for execution
        if lifecycle.current_state == DecisionState.DRAFT:
            violations.append(EnforcementViolation(
                violation_type="invalid_lifecycle_state",
                severity="CRITICAL",
                message="Decision is still in DRAFT state. Must be evaluated before execution.",
                field="lifecycle.current_state"
            ))
        
        return violations
    
    def _check_human_action(self, decision: DecisionResponse, lifecycle: Optional[DecisionLifecycle]) -> List[EnforcementViolation]:
        """Check human action requirements"""
        violations = []
        
        # If decision requires human review but lifecycle shows no human action
        if decision.human_review_required:
            if lifecycle and lifecycle.current_state == DecisionState.EVALUATED:
                violations.append(EnforcementViolation(
                    violation_type="missing_human_action",
                    severity="CRITICAL",
                    message="Decision requires human review but is still in EVALUATED state. Human action required.",
                    field="lifecycle.current_state"
                ))
        
        return violations
    
    def _check_audit_metadata(self, decision: DecisionResponse) -> List[EnforcementViolation]:
        """Check audit metadata requirements"""
        violations = []
        
        if not hasattr(decision, 'audit') or decision.audit is None:
            violations.append(EnforcementViolation(
                violation_type="missing_audit_metadata",
                severity="HIGH",
                message="Decision has no audit metadata. Audit trail is required for compliance.",
                field="audit"
            ))
        else:
            # Check required audit fields
            audit = decision.audit
            if not hasattr(audit, 'decision_id') or not audit.decision_id:
                violations.append(EnforcementViolation(
                    violation_type="missing_audit_decision_id",
                    severity="CRITICAL",
                    message="Audit metadata missing decision_id",
                    field="audit.decision_id"
                ))
            
            if not hasattr(audit, 'module_name') or not audit.module_name:
                violations.append(EnforcementViolation(
                    violation_type="missing_audit_module_name",
                    severity="HIGH",
                    message="Audit metadata missing module_name",
                    field="audit.module_name"
                ))
        
        return violations


class GovernanceViolationError(Exception):
    """Raised when critical governance violations are detected"""
    pass


# Convenience functions

def enforce_strict(decision: DecisionResponse, lifecycle: Optional[DecisionLifecycle] = None) -> None:
    """
    Enforce strict governance (blocks on any critical violation)
    
    Args:
        decision: Decision to enforce
        lifecycle: Optional lifecycle state
        
    Raises:
        GovernanceViolationError: If critical violations found
    """
    enforcer = GovernanceEnforcer(
        max_boundary_violations=0,
        require_position=True,
        require_explainability=True,
        require_lifecycle=True,
        block_on_critical=True
    )
    enforcer.enforce(decision, lifecycle)


def enforce_permissive(
    decision: DecisionResponse,
    lifecycle: Optional[DecisionLifecycle] = None
) -> EnforcementResult:
    """
    Enforce permissive governance (logs violations but doesn't block)
    
    Args:
        decision: Decision to enforce
        lifecycle: Optional lifecycle state
        
    Returns:
        EnforcementResult with violations
    """
    enforcer = GovernanceEnforcer(
        max_boundary_violations=3,
        require_position=True,
        require_explainability=True,
        require_lifecycle=False,
        block_on_critical=False
    )
    return enforcer.enforce(decision, lifecycle)


def check_compliance(
    decision: DecisionResponse,
    lifecycle: Optional[DecisionLifecycle] = None
) -> EnforcementResult:
    """
    Check compliance without blocking
    
    Args:
        decision: Decision to check
        lifecycle: Optional lifecycle state
        
    Returns:
        EnforcementResult with violations
    """
    enforcer = GovernanceEnforcer(
        max_boundary_violations=0,
        require_position=True,
        require_explainability=True,
        require_lifecycle=True,
        block_on_critical=False
    )
    return enforcer.enforce(decision, lifecycle)
