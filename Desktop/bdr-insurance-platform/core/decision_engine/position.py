"""
Decision Position Contract - Ownership & Liability

This module defines who owns, signs, and carries liability for insurance decisions.
Every decision MUST have a clear position contract - no silent ownership.

Author: BDR Platform Team
Created: 2026-01-20
Version: 1.0.0
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class DecisionDomain(str, Enum):
    """Insurance decision domains"""
    CLAIMS = "claims"
    UNDERWRITING = "underwriting"
    FRAUD = "fraud"
    ACTUARIAL = "actuarial"
    REINSURANCE = "reinsurance"
    COMPLIANCE = "compliance"


class RiskClass(str, Enum):
    """Risk classification for decision liability"""
    LOW = "low"  # < $10K exposure, routine decisions
    MEDIUM = "medium"  # $10K-$100K exposure, standard decisions
    HIGH = "high"  # $100K-$1M exposure, significant decisions
    CRITICAL = "critical"  # > $1M exposure, material decisions


class LiabilityScope(str, Enum):
    """Scope of liability for decision outcomes"""
    ADVISORY_ONLY = "advisory_only"  # Recommendation only, no binding liability
    OPERATIONAL = "operational"  # Standard operational liability
    FINANCIAL = "financial"  # Direct financial liability
    REGULATORY = "regulatory"  # Regulatory compliance liability
    FULL = "full"  # Complete liability (financial + regulatory + operational)


class EscalationPolicy(str, Enum):
    """Escalation policy for decision failures"""
    AUTO_REJECT = "auto_reject"  # Automatically reject on failure
    SUPERVISOR_REVIEW = "supervisor_review"  # Escalate to supervisor
    COMMITTEE_REVIEW = "committee_review"  # Escalate to decision committee
    EXECUTIVE_REVIEW = "executive_review"  # Escalate to executive level
    REGULATORY_NOTIFICATION = "regulatory_notification"  # Notify regulator


class OverrideAuthority(str, Enum):
    """Who can override this decision"""
    NONE = "none"  # Cannot be overridden
    PEER = "peer"  # Same role can override
    SUPERVISOR = "supervisor"  # Supervisor can override
    MANAGER = "manager"  # Manager can override
    EXECUTIVE = "executive"  # Executive can override
    REGULATORY = "regulatory"  # Only regulator can override


class RegulatoryContext(BaseModel):
    """Regulatory context for the decision"""
    jurisdiction: str = Field(..., description="Regulatory jurisdiction (e.g., 'US-CA', 'EU-GDPR')")
    applicable_regulations: List[str] = Field(
        default_factory=list,
        description="List of applicable regulations (e.g., ['IFRS 17', 'Solvency II'])"
    )
    compliance_requirements: List[str] = Field(
        default_factory=list,
        description="Specific compliance requirements"
    )
    audit_retention_years: int = Field(
        default=7,
        ge=1,
        le=50,
        description="Required audit retention period in years"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "jurisdiction": "US-CA",
                "applicable_regulations": ["California Insurance Code", "NAIC Model Laws"],
                "compliance_requirements": ["Fair Claims Settlement", "Unfair Practices Prevention"],
                "audit_retention_years": 7
            }
        }


class DecisionPosition(BaseModel):
    """
    Decision Position Contract - Defines ownership and liability
    
    Every DecisionResponse MUST include a DecisionPosition.
    No default values. No silent ownership.
    
    This contract answers:
    - Who owns the decision?
    - Who signs it?
    - Who carries liability?
    - Who can override?
    - Who escalates failures?
    """
    
    decision_id: str = Field(..., description="Unique decision identifier (must match DecisionResponse)")
    decision_domain: DecisionDomain = Field(..., description="Insurance domain for this decision")
    
    # Ownership
    owning_organization: str = Field(
        ...,
        min_length=1,
        description="Organization unit that owns this decision (e.g., 'Claims Department', 'Underwriting Division')"
    )
    decision_owner_role: str = Field(
        ...,
        min_length=1,
        description="Role responsible for this decision (e.g., 'Claims Adjuster', 'Senior Underwriter')"
    )
    signatory_role: str = Field(
        ...,
        min_length=1,
        description="Role authorized to sign/approve this decision (may differ from owner)"
    )
    
    # Liability
    liability_scope: LiabilityScope = Field(..., description="Scope of liability for this decision")
    risk_class: RiskClass = Field(..., description="Risk classification for liability purposes")
    
    # Governance
    escalation_policy: EscalationPolicy = Field(..., description="Policy for escalating decision failures")
    override_authority: OverrideAuthority = Field(..., description="Who can override this decision")
    
    # Regulatory
    regulatory_context: RegulatoryContext = Field(..., description="Regulatory context and requirements")
    
    # Metadata
    position_created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this position was established"
    )
    position_version: str = Field(
        default="1.0.0",
        description="Version of the position contract"
    )
    
    @field_validator('decision_owner_role', 'signatory_role', 'owning_organization')
    @classmethod
    def validate_no_generic_roles(cls, v: str) -> str:
        """Prevent generic or placeholder roles"""
        forbidden = ['tbd', 'todo', 'unknown', 'default', 'system', 'auto']
        if v.lower() in forbidden:
            raise ValueError(f"Generic role '{v}' not allowed - must specify actual role/organization")
        return v
    
    def requires_executive_approval(self) -> bool:
        """Check if this decision requires executive-level approval"""
        return (
            self.risk_class == RiskClass.CRITICAL or
            self.liability_scope == LiabilityScope.FULL or
            self.override_authority == OverrideAuthority.EXECUTIVE
        )
    
    def requires_regulatory_notification(self) -> bool:
        """Check if this decision requires regulatory notification"""
        return (
            self.escalation_policy == EscalationPolicy.REGULATORY_NOTIFICATION or
            self.override_authority == OverrideAuthority.REGULATORY
        )
    
    def is_high_liability(self) -> bool:
        """Check if this is a high-liability decision"""
        return self.risk_class in [RiskClass.HIGH, RiskClass.CRITICAL]
    
    def can_be_overridden_by(self, actor_role: str) -> bool:
        """
        Check if a given role can override this decision
        
        Args:
            actor_role: Role attempting to override (e.g., 'supervisor', 'manager')
            
        Returns:
            True if the role has override authority
        """
        if self.override_authority == OverrideAuthority.NONE:
            return False
        
        # Simple role hierarchy check (in production, use proper RBAC)
        role_hierarchy = {
            OverrideAuthority.PEER: ['peer'],
            OverrideAuthority.SUPERVISOR: ['peer', 'supervisor'],
            OverrideAuthority.MANAGER: ['peer', 'supervisor', 'manager'],
            OverrideAuthority.EXECUTIVE: ['peer', 'supervisor', 'manager', 'executive'],
            OverrideAuthority.REGULATORY: ['regulatory']
        }
        
        allowed_roles = role_hierarchy.get(self.override_authority, [])
        return actor_role.lower() in allowed_roles
    
    def get_audit_retention_date(self) -> datetime:
        """Calculate when this decision's audit trail can be purged"""
        from datetime import timedelta
        retention_days = self.regulatory_context.audit_retention_years * 365
        return self.position_created_at + timedelta(days=retention_days)
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "fnol-2026-01-20-abc123",
                "decision_domain": "claims",
                "owning_organization": "Claims Department - Auto Division",
                "decision_owner_role": "Claims Adjuster",
                "signatory_role": "Senior Claims Adjuster",
                "liability_scope": "operational",
                "risk_class": "medium",
                "escalation_policy": "supervisor_review",
                "override_authority": "supervisor",
                "regulatory_context": {
                    "jurisdiction": "US-CA",
                    "applicable_regulations": ["California Insurance Code"],
                    "compliance_requirements": ["Fair Claims Settlement"],
                    "audit_retention_years": 7
                }
            }
        }


# Position factory functions for common scenarios

def create_claims_position(
    decision_id: str,
    claim_amount: float,
    jurisdiction: str = "US-CA"
) -> DecisionPosition:
    """
    Create a standard claims decision position
    
    Args:
        decision_id: Unique decision identifier
        claim_amount: Claim amount in USD
        jurisdiction: Regulatory jurisdiction
        
    Returns:
        DecisionPosition configured for claims decisions
    """
    # Determine risk class based on claim amount
    if claim_amount < 10000:
        risk_class = RiskClass.LOW
        liability = LiabilityScope.OPERATIONAL
        escalation = EscalationPolicy.AUTO_REJECT
        override = OverrideAuthority.PEER
    elif claim_amount < 100000:
        risk_class = RiskClass.MEDIUM
        liability = LiabilityScope.OPERATIONAL
        escalation = EscalationPolicy.SUPERVISOR_REVIEW
        override = OverrideAuthority.SUPERVISOR
    elif claim_amount < 1000000:
        risk_class = RiskClass.HIGH
        liability = LiabilityScope.FINANCIAL
        escalation = EscalationPolicy.COMMITTEE_REVIEW
        override = OverrideAuthority.MANAGER
    else:
        risk_class = RiskClass.CRITICAL
        liability = LiabilityScope.FULL
        escalation = EscalationPolicy.EXECUTIVE_REVIEW
        override = OverrideAuthority.EXECUTIVE
    
    return DecisionPosition(
        decision_id=decision_id,
        decision_domain=DecisionDomain.CLAIMS,
        owning_organization="Claims Department",
        decision_owner_role="Claims Adjuster",
        signatory_role="Senior Claims Adjuster" if risk_class in [RiskClass.LOW, RiskClass.MEDIUM] else "Claims Manager",
        liability_scope=liability,
        risk_class=risk_class,
        escalation_policy=escalation,
        override_authority=override,
        regulatory_context=RegulatoryContext(
            jurisdiction=jurisdiction,
            applicable_regulations=["California Insurance Code", "NAIC Model Laws"],
            compliance_requirements=["Fair Claims Settlement", "Unfair Practices Prevention"],
            audit_retention_years=7
        )
    )


def create_underwriting_position(
    decision_id: str,
    coverage_amount: float,
    jurisdiction: str = "US-CA"
) -> DecisionPosition:
    """Create a standard underwriting decision position"""
    if coverage_amount < 100000:
        risk_class = RiskClass.LOW
    elif coverage_amount < 1000000:
        risk_class = RiskClass.MEDIUM
    elif coverage_amount < 10000000:
        risk_class = RiskClass.HIGH
    else:
        risk_class = RiskClass.CRITICAL
    
    return DecisionPosition(
        decision_id=decision_id,
        decision_domain=DecisionDomain.UNDERWRITING,
        owning_organization="Underwriting Division",
        decision_owner_role="Underwriter",
        signatory_role="Senior Underwriter" if risk_class in [RiskClass.LOW, RiskClass.MEDIUM] else "Underwriting Manager",
        liability_scope=LiabilityScope.FINANCIAL if risk_class in [RiskClass.HIGH, RiskClass.CRITICAL] else LiabilityScope.OPERATIONAL,
        risk_class=risk_class,
        escalation_policy=EscalationPolicy.SUPERVISOR_REVIEW if risk_class == RiskClass.LOW else EscalationPolicy.COMMITTEE_REVIEW,
        override_authority=OverrideAuthority.SUPERVISOR if risk_class in [RiskClass.LOW, RiskClass.MEDIUM] else OverrideAuthority.MANAGER,
        regulatory_context=RegulatoryContext(
            jurisdiction=jurisdiction,
            applicable_regulations=["State Insurance Regulations", "NAIC Guidelines"],
            compliance_requirements=["Risk Assessment Standards", "Fair Underwriting Practices"],
            audit_retention_years=10
        )
    )


def create_fraud_position(
    decision_id: str,
    fraud_score: float,
    jurisdiction: str = "US-CA"
) -> DecisionPosition:
    """Create a standard fraud detection decision position"""
    # Fraud decisions are always high-risk due to legal implications
    risk_class = RiskClass.HIGH if fraud_score < 0.9 else RiskClass.CRITICAL
    
    return DecisionPosition(
        decision_id=decision_id,
        decision_domain=DecisionDomain.FRAUD,
        owning_organization="Special Investigations Unit",
        decision_owner_role="Fraud Investigator",
        signatory_role="SIU Manager",
        liability_scope=LiabilityScope.FULL,  # Fraud has full liability
        risk_class=risk_class,
        escalation_policy=EscalationPolicy.COMMITTEE_REVIEW,
        override_authority=OverrideAuthority.EXECUTIVE,  # Fraud overrides require executive approval
        regulatory_context=RegulatoryContext(
            jurisdiction=jurisdiction,
            applicable_regulations=["Insurance Fraud Prevention Act", "Criminal Code"],
            compliance_requirements=["Evidence Chain of Custody", "Due Process", "Privacy Protection"],
            audit_retention_years=10  # Fraud cases require longer retention
        )
    )
