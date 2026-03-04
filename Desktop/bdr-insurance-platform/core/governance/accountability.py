"""Accountability Scope - Defines what owners are responsible for.

Maps decision types to accountability scopes, defining:
- Allowed actions
- Forbidden actions
- Maximum impact levels
- Financial exposure limits
- Regulatory sensitivity
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

from core.decision_engine.enums import DecisionType


class ImpactLevel(int, Enum):
    """Impact level classification for decisions.
    
    Levels:
    1 = MINIMAL: No financial impact, informational only
    2 = LOW: < $1,000 financial impact
    3 = MEDIUM: $1,000 - $50,000 financial impact
    4 = HIGH: $50,000 - $500,000 financial impact
    5 = CRITICAL: > $500,000 financial impact or regulatory significance
    """
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


class RegulatoryClass(str, Enum):
    """Regulatory sensitivity classification."""
    NONE = "none"
    STANDARD = "standard"
    SENSITIVE = "sensitive"
    HIGHLY_REGULATED = "highly_regulated"


@dataclass(frozen=True)
class AccountabilityScope:
    """Defines what the owner is responsible for.
    
    Attributes:
        decision_type: Type of decision (advisory, bounded, simulation)
        allowed_actions: List of actions the owner can perform
        forbidden_actions: List of actions explicitly forbidden
        max_impact_level: Maximum impact level allowed (1-5)
        max_financial_exposure: Maximum financial exposure in USD
        regulatory_class: Regulatory sensitivity classification
        requires_dual_approval: Whether dual approval is required
        audit_retention_days: How long audit records must be retained
    
    Raises:
        ValueError: If scope configuration is invalid
    """
    
    decision_type: DecisionType
    allowed_actions: List[str]
    forbidden_actions: List[str]
    max_impact_level: ImpactLevel
    max_financial_exposure: Optional[float] = None
    regulatory_class: RegulatoryClass = RegulatoryClass.STANDARD
    requires_dual_approval: bool = False
    audit_retention_days: int = 2555  # 7 years default
    
    def __post_init__(self):
        """Validate accountability scope."""
        # Validate no overlap between allowed and forbidden
        overlap = set(self.allowed_actions) & set(self.forbidden_actions)
        if overlap:
            raise ValueError(
                f"Actions cannot be both allowed and forbidden: {overlap}"
            )
        
        # Validate financial exposure matches impact level
        if self.max_financial_exposure is not None:
            if self.max_impact_level == ImpactLevel.MINIMAL and self.max_financial_exposure > 0:
                raise ValueError(
                    "MINIMAL impact level must have zero financial exposure"
                )
            
            if self.max_impact_level == ImpactLevel.LOW and self.max_financial_exposure > 1000:
                raise ValueError(
                    "LOW impact level cannot exceed $1,000 financial exposure"
                )
            
            if self.max_impact_level == ImpactLevel.MEDIUM and self.max_financial_exposure > 50000:
                raise ValueError(
                    "MEDIUM impact level cannot exceed $50,000 financial exposure"
                )
            
            if self.max_impact_level == ImpactLevel.HIGH and self.max_financial_exposure > 500000:
                raise ValueError(
                    "HIGH impact level cannot exceed $500,000 financial exposure"
                )
        
        # Validate decision type constraints
        if self.decision_type == DecisionType.ADVISORY:
            if "auto_approve" in self.allowed_actions:
                raise ValueError(
                    "ADVISORY decisions cannot have 'auto_approve' in allowed_actions"
                )
        
        if self.decision_type == DecisionType.SIMULATION:
            if self.max_financial_exposure is not None and self.max_financial_exposure > 0:
                raise ValueError(
                    "SIMULATION decisions must have zero financial exposure"
                )
        
        # Validate audit retention
        if self.audit_retention_days < 365:
            raise ValueError(
                "Audit retention must be at least 365 days (1 year)"
            )
        
        # Validate highly regulated decisions
        if self.regulatory_class == RegulatoryClass.HIGHLY_REGULATED:
            if self.audit_retention_days < 2555:  # 7 years
                raise ValueError(
                    "Highly regulated decisions require at least 7 years audit retention"
                )
    
    def is_action_allowed(self, action: str) -> bool:
        """Check if an action is allowed.
        
        Args:
            action: Action to check
        
        Returns:
            True if action is allowed, False otherwise
        """
        if action in self.forbidden_actions:
            return False
        return action in self.allowed_actions
    
    def validate_financial_exposure(self, amount: float) -> tuple[bool, Optional[str]]:
        """Validate if a financial exposure is within scope.
        
        Args:
            amount: Financial exposure amount in USD
        
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        if self.max_financial_exposure is None:
            return True, None
        
        if amount > self.max_financial_exposure:
            return False, (
                f"Financial exposure ${amount:,.2f} exceeds maximum "
                f"${self.max_financial_exposure:,.2f} for {self.decision_type.value} decisions"
            )
        
        return True, None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for audit logging."""
        return {
            "decision_type": self.decision_type.value,
            "allowed_actions": self.allowed_actions,
            "forbidden_actions": self.forbidden_actions,
            "max_impact_level": self.max_impact_level.value,
            "max_financial_exposure": self.max_financial_exposure,
            "regulatory_class": self.regulatory_class.value,
            "requires_dual_approval": self.requires_dual_approval,
            "audit_retention_days": self.audit_retention_days,
        }


# Predefined scopes for common decision types

ADVISORY_SCOPE = AccountabilityScope(
    decision_type=DecisionType.ADVISORY,
    allowed_actions=[
        "provide_recommendation",
        "flag_for_review",
        "generate_report",
        "calculate_risk_score",
    ],
    forbidden_actions=[
        "auto_approve",
        "auto_reject",
        "disburse_funds",
        "modify_policy",
    ],
    max_impact_level=ImpactLevel.CRITICAL,
    max_financial_exposure=None,  # Advisory has no direct financial impact
    regulatory_class=RegulatoryClass.STANDARD,
    requires_dual_approval=False,
)

BOUNDED_LOW_SCOPE = AccountabilityScope(
    decision_type=DecisionType.BOUNDED,
    allowed_actions=[
        "auto_approve",
        "flag_for_review",
        "assign_to_adjuster",
        "generate_report",
    ],
    forbidden_actions=[
        "disburse_funds",
        "modify_policy",
        "override_fraud_flag",
    ],
    max_impact_level=ImpactLevel.LOW,
    max_financial_exposure=1000.0,
    regulatory_class=RegulatoryClass.STANDARD,
    requires_dual_approval=False,
)

BOUNDED_MEDIUM_SCOPE = AccountabilityScope(
    decision_type=DecisionType.BOUNDED,
    allowed_actions=[
        "auto_approve",
        "flag_for_review",
        "assign_to_adjuster",
        "generate_report",
        "request_additional_info",
    ],
    forbidden_actions=[
        "disburse_funds",
        "modify_policy",
        "override_fraud_flag",
    ],
    max_impact_level=ImpactLevel.MEDIUM,
    max_financial_exposure=50000.0,
    regulatory_class=RegulatoryClass.SENSITIVE,
    requires_dual_approval=False,
)

BOUNDED_HIGH_SCOPE = AccountabilityScope(
    decision_type=DecisionType.BOUNDED,
    allowed_actions=[
        "flag_for_review",
        "assign_to_senior_adjuster",
        "generate_report",
        "request_additional_info",
        "escalate_to_committee",
    ],
    forbidden_actions=[
        "auto_approve",
        "auto_reject",
        "disburse_funds",
        "modify_policy",
    ],
    max_impact_level=ImpactLevel.HIGH,
    max_financial_exposure=500000.0,
    regulatory_class=RegulatoryClass.HIGHLY_REGULATED,
    requires_dual_approval=True,
    audit_retention_days=2555,  # 7 years
)

SIMULATION_SCOPE = AccountabilityScope(
    decision_type=DecisionType.SIMULATION,
    allowed_actions=[
        "run_simulation",
        "generate_report",
        "calculate_scenarios",
        "export_results",
    ],
    forbidden_actions=[
        "auto_approve",
        "auto_reject",
        "disburse_funds",
        "modify_policy",
        "assign_to_adjuster",
    ],
    max_impact_level=ImpactLevel.MINIMAL,
    max_financial_exposure=0.0,
    regulatory_class=RegulatoryClass.NONE,
    requires_dual_approval=False,
    audit_retention_days=365,  # 1 year minimum
)


def get_scope_for_decision_type(
    decision_type: DecisionType,
    financial_exposure: Optional[float] = None,
) -> AccountabilityScope:
    """Get the appropriate accountability scope for a decision type.
    
    Args:
        decision_type: Type of decision
        financial_exposure: Optional financial exposure amount
    
    Returns:
        Appropriate AccountabilityScope
    """
    if decision_type == DecisionType.ADVISORY:
        return ADVISORY_SCOPE
    
    if decision_type == DecisionType.SIMULATION:
        return SIMULATION_SCOPE
    
    if decision_type == DecisionType.BOUNDED:
        if financial_exposure is None:
            return BOUNDED_LOW_SCOPE
        
        if financial_exposure <= 1000:
            return BOUNDED_LOW_SCOPE
        elif financial_exposure <= 50000:
            return BOUNDED_MEDIUM_SCOPE
        else:
            return BOUNDED_HIGH_SCOPE
    
    raise ValueError(f"Unknown decision type: {decision_type}")
