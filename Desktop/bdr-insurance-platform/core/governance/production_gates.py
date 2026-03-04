"""Production Gates Module

This module implements production readiness gates that must be passed before
decisions can be executed in production environments. Gates enforce:
- Pre-execution validation
- Post-execution verification
- Deployment readiness checks
- Environment-specific rules

All gates are immutable, auditable, and enforceable at runtime.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4

from .authority import DecisionAuthority, DecisionSeverity
from .ownership import AccountabilityChain
from .accountability import AccountabilityScope


class GateType(Enum):
    """Types of production gates."""
    PRE_EXECUTION = "pre_execution"  # Must pass before decision execution
    POST_EXECUTION = "post_execution"  # Must pass after decision execution
    DEPLOYMENT = "deployment"  # Must pass before deployment to production
    MONITORING = "monitoring"  # Continuous monitoring gate
    AUDIT = "audit"  # Audit trail completeness gate


class GateStatus(Enum):
    """Status of a production gate."""
    PENDING = "pending"  # Gate not yet evaluated
    PASSED = "passed"  # Gate passed successfully
    FAILED = "failed"  # Gate failed validation
    BYPASSED = "bypassed"  # Gate bypassed (requires authority)
    SKIPPED = "skipped"  # Gate skipped (not applicable)


class GateSeverity(Enum):
    """Severity level of gate failure."""
    INFO = "info"  # Informational only
    WARNING = "warning"  # Should be addressed but not blocking
    ERROR = "error"  # Blocking error, must be fixed
    CRITICAL = "critical"  # Critical failure, immediate action required


@dataclass(frozen=True)
class ProductionGate:
    """Immutable production gate definition.
    
    A production gate is a checkpoint that must be passed before a decision
    can be executed in production. Gates enforce quality, safety, and
    compliance requirements.
    
    Attributes:
        gate_id: Unique identifier for this gate
        gate_type: Type of gate (pre/post execution, deployment, etc.)
        name: Human-readable gate name
        description: Detailed description of what this gate checks
        severity: Severity level if gate fails
        required_in_production: Whether this gate is mandatory in production
        required_in_staging: Whether this gate is mandatory in staging
        required_in_dev: Whether this gate is mandatory in development
        can_bypass: Whether this gate can be bypassed with proper authority
        bypass_requires_authority: Minimum authority level required to bypass
        validation_function: Name of the validation function to execute
        metadata: Additional gate-specific metadata
    """
    gate_id: str
    gate_type: GateType
    name: str
    description: str
    severity: GateSeverity
    required_in_production: bool
    required_in_staging: bool
    required_in_dev: bool
    can_bypass: bool
    bypass_requires_authority: Optional[DecisionSeverity]
    validation_function: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate gate configuration."""
        if not self.gate_id:
            raise ValueError("gate_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if not self.validation_function:
            raise ValueError("validation_function cannot be empty")
        
        # If gate cannot be bypassed, bypass_requires_authority should be None
        if not self.can_bypass and self.bypass_requires_authority is not None:
            raise ValueError("Non-bypassable gate cannot have bypass_requires_authority")
        
        # If gate can be bypassed, bypass_requires_authority must be set
        if self.can_bypass and self.bypass_requires_authority is None:
            raise ValueError("Bypassable gate must specify bypass_requires_authority")


@dataclass(frozen=True)
class ProductionGateResult:
    """Result of a production gate evaluation.
    
    Attributes:
        gate: The gate that was evaluated
        status: Status of the gate evaluation
        passed: Whether the gate passed (convenience field)
        evaluated_at: Timestamp of evaluation
        evaluated_by: Who/what evaluated the gate
        failure_reason: Reason for failure (if status is FAILED)
        bypass_reason: Reason for bypass (if status is BYPASSED)
        bypass_authority: Authority that approved bypass (if bypassed)
        validation_details: Detailed validation results
        metadata: Additional result metadata
    """
    gate: ProductionGate
    status: GateStatus
    passed: bool
    evaluated_at: datetime
    evaluated_by: str
    failure_reason: Optional[str] = None
    bypass_reason: Optional[str] = None
    bypass_authority: Optional[DecisionAuthority] = None
    validation_details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate gate result."""
        # If status is FAILED, must have failure_reason
        if self.status == GateStatus.FAILED and not self.failure_reason:
            raise ValueError("Failed gate must have failure_reason")
        
        # If status is BYPASSED, must have bypass_reason and bypass_authority
        if self.status == GateStatus.BYPASSED:
            if not self.bypass_reason:
                raise ValueError("Bypassed gate must have bypass_reason")
            if not self.bypass_authority:
                raise ValueError("Bypassed gate must have bypass_authority")
        
        # passed field must match status
        expected_passed = self.status in (GateStatus.PASSED, GateStatus.BYPASSED, GateStatus.SKIPPED)
        if self.passed != expected_passed:
            raise ValueError(f"passed={self.passed} inconsistent with status={self.status}")


@dataclass(frozen=True)
class GateEvaluationContext:
    """Context for evaluating production gates.
    
    Attributes:
        environment: Current environment (dev, staging, production)
        decision_severity: Severity of the decision being gated
        authority: Authority executing the decision
        ownership: Ownership chain for the decision
        accountability_scope: Accountability scope for the decision
        metadata: Additional context metadata
    """
    environment: str
    decision_severity: DecisionSeverity
    authority: DecisionAuthority
    ownership: AccountabilityChain
    accountability_scope: AccountabilityScope
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate evaluation context."""
        valid_environments = {"dev", "development", "staging", "stage", "production", "prod"}
        if self.environment.lower() not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}")


# Predefined Production Gates

OWNERSHIP_GATE = ProductionGate(
    gate_id="gate_ownership_required",
    gate_type=GateType.PRE_EXECUTION,
    name="Ownership Required",
    description="Decision must have valid ownership chain with ultimate accountable entity",
    severity=GateSeverity.CRITICAL,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=False,
    bypass_requires_authority=None,
    validation_function="validate_ownership_present",
    metadata={"phase": "2.1", "category": "governance"}
)

AUTHORITY_GATE = ProductionGate(
    gate_id="gate_authority_required",
    gate_type=GateType.PRE_EXECUTION,
    name="Authority Required",
    description="Decision must have valid authority with appropriate permissions",
    severity=GateSeverity.CRITICAL,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=False,
    bypass_requires_authority=None,
    validation_function="validate_authority_present",
    metadata={"phase": "2.1.1", "category": "governance"}
)

SEVERITY_MATCH_GATE = ProductionGate(
    gate_id="gate_severity_match",
    gate_type=GateType.PRE_EXECUTION,
    name="Severity Match",
    description="Decision severity must not exceed authority maximum severity",
    severity=GateSeverity.ERROR,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=True,
    bypass_requires_authority=DecisionSeverity.EMERGENCY,
    validation_function="validate_severity_match",
    metadata={"phase": "2.1.1", "category": "authority"}
)

HUMAN_SIGNATURE_GATE = ProductionGate(
    gate_id="gate_human_signature",
    gate_type=GateType.PRE_EXECUTION,
    name="Human Signature Required",
    description="High-severity decisions must have human signature when required",
    severity=GateSeverity.ERROR,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=True,
    bypass_requires_authority=DecisionSeverity.CRITICAL,
    validation_function="validate_human_signature",
    metadata={"phase": "2.1.1", "category": "authority"}
)

AUDIT_TRAIL_GATE = ProductionGate(
    gate_id="gate_audit_trail",
    gate_type=GateType.POST_EXECUTION,
    name="Audit Trail Complete",
    description="Decision must have complete audit trail with all required metadata",
    severity=GateSeverity.ERROR,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=False,
    bypass_requires_authority=None,
    validation_function="validate_audit_trail",
    metadata={"phase": "2.1", "category": "audit"}
)

COMPLIANCE_GATE = ProductionGate(
    gate_id="gate_compliance_check",
    gate_type=GateType.PRE_EXECUTION,
    name="Compliance Check",
    description="Decision must pass all applicable regulatory compliance checks",
    severity=GateSeverity.CRITICAL,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=False,
    can_bypass=True,
    bypass_requires_authority=DecisionSeverity.EMERGENCY,
    validation_function="validate_compliance",
    metadata={"phase": "2.2", "category": "compliance"}
)

BOUNDARY_GATE = ProductionGate(
    gate_id="gate_boundary_check",
    gate_type=GateType.PRE_EXECUTION,
    name="Boundary Check",
    description="Decision must respect all defined boundaries and constraints",
    severity=GateSeverity.ERROR,
    required_in_production=True,
    required_in_staging=True,
    required_in_dev=True,
    can_bypass=True,
    bypass_requires_authority=DecisionSeverity.CRITICAL,
    validation_function="validate_boundaries",
    metadata={"phase": "1.0", "category": "boundaries"}
)

DEPLOYMENT_READINESS_GATE = ProductionGate(
    gate_id="gate_deployment_readiness",
    gate_type=GateType.DEPLOYMENT,
    name="Deployment Readiness",
    description="System must pass all deployment readiness checks before production deployment",
    severity=GateSeverity.CRITICAL,
    required_in_production=True,
    required_in_staging=False,
    required_in_dev=False,
    can_bypass=True,
    bypass_requires_authority=DecisionSeverity.EMERGENCY,
    validation_function="validate_deployment_readiness",
    metadata={"phase": "2.2", "category": "deployment"}
)

# Gate Collections

PRE_EXECUTION_GATES = [
    OWNERSHIP_GATE,
    AUTHORITY_GATE,
    SEVERITY_MATCH_GATE,
    HUMAN_SIGNATURE_GATE,
    COMPLIANCE_GATE,
    BOUNDARY_GATE,
]

POST_EXECUTION_GATES = [
    AUDIT_TRAIL_GATE,
]

DEPLOYMENT_GATES = [
    DEPLOYMENT_READINESS_GATE,
]

ALL_GATES = PRE_EXECUTION_GATES + POST_EXECUTION_GATES + DEPLOYMENT_GATES


def get_required_gates(
    gate_type: GateType,
    environment: str
) -> List[ProductionGate]:
    """Get all required gates for a given type and environment.
    
    Args:
        gate_type: Type of gates to retrieve
        environment: Current environment (dev, staging, production)
    
    Returns:
        List of required gates for the given context
    """
    env_lower = environment.lower()
    is_production = env_lower in ("production", "prod")
    is_staging = env_lower in ("staging", "stage")
    is_dev = env_lower in ("dev", "development")
    
    required_gates = []
    for gate in ALL_GATES:
        if gate.gate_type != gate_type:
            continue
        
        if is_production and gate.required_in_production:
            required_gates.append(gate)
        elif is_staging and gate.required_in_staging:
            required_gates.append(gate)
        elif is_dev and gate.required_in_dev:
            required_gates.append(gate)
    
    return required_gates


def can_bypass_gate(
    gate: ProductionGate,
    authority: DecisionAuthority
) -> bool:
    """Check if an authority can bypass a gate.
    
    Args:
        gate: Gate to check
        authority: Authority attempting to bypass
    
    Returns:
        True if authority can bypass the gate, False otherwise
    """
    if not gate.can_bypass:
        return False
    
    if gate.bypass_requires_authority is None:
        return False
    
    # Check if authority's max severity is >= required bypass severity
    severity_order = [
        DecisionSeverity.ROUTINE,
        DecisionSeverity.ELEVATED,
        DecisionSeverity.CRITICAL,
        DecisionSeverity.EMERGENCY,
        DecisionSeverity.CATASTROPHIC,
    ]
    
    authority_level = severity_order.index(authority.max_decision_severity)
    required_level = severity_order.index(gate.bypass_requires_authority)
    
    return authority_level >= required_level


def create_gate_result(
    gate: ProductionGate,
    status: GateStatus,
    evaluated_by: str,
    failure_reason: Optional[str] = None,
    bypass_reason: Optional[str] = None,
    bypass_authority: Optional[DecisionAuthority] = None,
    validation_details: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ProductionGateResult:
    """Create a production gate result.
    
    Args:
        gate: Gate that was evaluated
        status: Status of the evaluation
        evaluated_by: Who/what evaluated the gate
        failure_reason: Reason for failure (if failed)
        bypass_reason: Reason for bypass (if bypassed)
        bypass_authority: Authority that approved bypass (if bypassed)
        validation_details: Detailed validation results
        metadata: Additional metadata
    
    Returns:
        ProductionGateResult instance
    """
    passed = status in (GateStatus.PASSED, GateStatus.BYPASSED, GateStatus.SKIPPED)
    
    return ProductionGateResult(
        gate=gate,
        status=status,
        passed=passed,
        evaluated_at=datetime.utcnow(),
        evaluated_by=evaluated_by,
        failure_reason=failure_reason,
        bypass_reason=bypass_reason,
        bypass_authority=bypass_authority,
        validation_details=validation_details or {},
        metadata=metadata or {}
    )


# ============================================================================
# Environment-Specific Configuration
# ============================================================================

class EnvironmentType(Enum):
    """Environment types for deployment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass(frozen=True)
class EnvironmentConfig:
    """Environment-specific configuration for governance rules.
    
    Attributes:
        environment: Environment type
        enforce_ownership: Whether to enforce ownership requirements
        enforce_authority: Whether to enforce authority requirements
        enforce_gates: Whether to enforce production gates
        allow_gate_bypass: Whether gates can be bypassed
        require_human_signature_threshold: Severity threshold requiring human signature
        require_committee_threshold: Severity threshold requiring committee approval
        max_system_authority_severity: Maximum severity for system-owned decisions
        audit_all_decisions: Whether to audit all decisions (vs. only high-severity)
        enable_escalation: Whether to enable automatic escalation
        compliance_frameworks: List of compliance frameworks to enforce
        metadata: Additional environment-specific metadata
    """
    environment: EnvironmentType
    enforce_ownership: bool
    enforce_authority: bool
    enforce_gates: bool
    allow_gate_bypass: bool
    require_human_signature_threshold: DecisionSeverity
    require_committee_threshold: DecisionSeverity
    max_system_authority_severity: DecisionSeverity
    audit_all_decisions: bool
    enable_escalation: bool
    compliance_frameworks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate environment configuration."""
        # Production must enforce all governance rules
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.enforce_ownership:
                raise ValueError("Production must enforce ownership")
            if not self.enforce_authority:
                raise ValueError("Production must enforce authority")
            if not self.enforce_gates:
                raise ValueError("Production must enforce gates")
            if not self.audit_all_decisions:
                raise ValueError("Production must audit all decisions")


# Predefined Environment Configurations

DEVELOPMENT_CONFIG = EnvironmentConfig(
    environment=EnvironmentType.DEVELOPMENT,
    enforce_ownership=False,  # Optional in dev
    enforce_authority=False,  # Optional in dev
    enforce_gates=False,  # Optional in dev
    allow_gate_bypass=True,  # Can bypass in dev
    require_human_signature_threshold=DecisionSeverity.CATASTROPHIC,  # Very high threshold
    require_committee_threshold=DecisionSeverity.CATASTROPHIC,  # Very high threshold
    max_system_authority_severity=DecisionSeverity.CRITICAL,  # Relaxed in dev
    audit_all_decisions=False,  # Only audit high-severity in dev
    enable_escalation=False,  # No escalation in dev
    compliance_frameworks=[],  # No compliance checks in dev
    metadata={"description": "Development environment with relaxed governance"}
)

STAGING_CONFIG = EnvironmentConfig(
    environment=EnvironmentType.STAGING,
    enforce_ownership=True,  # Enforce in staging
    enforce_authority=True,  # Enforce in staging
    enforce_gates=True,  # Enforce in staging
    allow_gate_bypass=True,  # Can bypass with authority
    require_human_signature_threshold=DecisionSeverity.ELEVATED,  # Lower threshold
    require_committee_threshold=DecisionSeverity.EMERGENCY,  # High threshold
    max_system_authority_severity=DecisionSeverity.ROUTINE,  # Restricted in staging
    audit_all_decisions=True,  # Audit all in staging
    enable_escalation=True,  # Enable escalation in staging
    compliance_frameworks=["ISO27001"],  # Basic compliance in staging
    metadata={"description": "Staging environment with production-like governance"}
)

PRODUCTION_CONFIG = EnvironmentConfig(
    environment=EnvironmentType.PRODUCTION,
    enforce_ownership=True,  # MANDATORY in production
    enforce_authority=True,  # MANDATORY in production
    enforce_gates=True,  # MANDATORY in production
    allow_gate_bypass=False,  # NO bypass in production (except emergency)
    require_human_signature_threshold=DecisionSeverity.ELEVATED,  # Low threshold
    require_committee_threshold=DecisionSeverity.EMERGENCY,  # High threshold
    max_system_authority_severity=DecisionSeverity.ROUTINE,  # Heavily restricted
    audit_all_decisions=True,  # MANDATORY audit all
    enable_escalation=True,  # MANDATORY escalation
    compliance_frameworks=["GDPR", "SOC2", "ISO27001", "PCI-DSS"],  # Full compliance
    metadata={"description": "Production environment with strict governance"}
)


def get_environment_config(environment: str) -> EnvironmentConfig:
    """Get configuration for a given environment.
    
    Args:
        environment: Environment name (dev, staging, production)
    
    Returns:
        EnvironmentConfig for the given environment
    
    Raises:
        ValueError: If environment is not recognized
    """
    env_lower = environment.lower()
    
    if env_lower in ("dev", "development"):
        return DEVELOPMENT_CONFIG
    elif env_lower in ("staging", "stage"):
        return STAGING_CONFIG
    elif env_lower in ("production", "prod"):
        return PRODUCTION_CONFIG
    else:
        raise ValueError(f"Unknown environment: {environment}")


def detect_environment() -> EnvironmentType:
    """Detect current environment from system environment variables.
    
    Returns:
        Detected environment type
    """
    import os
    
    # Check common environment variable names
    env_vars = [
        "ENVIRONMENT",
        "ENV",
        "DEPLOYMENT_ENV",
        "APP_ENV",
        "STAGE",
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "").lower()
        if value in ("dev", "development"):
            return EnvironmentType.DEVELOPMENT
        elif value in ("staging", "stage"):
            return EnvironmentType.STAGING
        elif value in ("production", "prod"):
            return EnvironmentType.PRODUCTION
    
    # Default to development if not specified
    return EnvironmentType.DEVELOPMENT


def should_enforce_rule(
    rule_name: str,
    environment: str,
    config: Optional[EnvironmentConfig] = None
) -> bool:
    """Check if a governance rule should be enforced in the given environment.
    
    Args:
        rule_name: Name of the rule (ownership, authority, gates, etc.)
        environment: Environment name
        config: Optional pre-loaded environment config
    
    Returns:
        True if rule should be enforced, False otherwise
    """
    if config is None:
        config = get_environment_config(environment)
    
    rule_map = {
        "ownership": config.enforce_ownership,
        "authority": config.enforce_authority,
        "gates": config.enforce_gates,
        "escalation": config.enable_escalation,
        "audit": config.audit_all_decisions,
    }
    
    return rule_map.get(rule_name, False)
