"""Regulatory Compliance Module - Phase 2.2

This module implements regulatory compliance checks for decisions.
Supports multiple compliance frameworks:
- GDPR (General Data Protection Regulation)
- SOC2 (Service Organization Control 2)
- ISO27001 (Information Security Management)
- PCI-DSS (Payment Card Industry Data Security Standard)
- HIPAA (Health Insurance Portability and Accountability Act)

All compliance checks are auditable and enforceable at runtime.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Set
from uuid import uuid4

from .authority import DecisionAuthority, DecisionSeverity
from .ownership import AccountabilityChain


class RegulatoryFramework(Enum):
    """Supported regulatory frameworks."""
    GDPR = "gdpr"  # EU General Data Protection Regulation
    SOC2 = "soc2"  # Service Organization Control 2
    ISO27001 = "iso27001"  # Information Security Management
    PCI_DSS = "pci_dss"  # Payment Card Industry Data Security
    HIPAA = "hipaa"  # Health Insurance Portability and Accountability
    GLBA = "glba"  # Gramm-Leach-Bliley Act
    CCPA = "ccpa"  # California Consumer Privacy Act
    FERPA = "ferpa"  # Family Educational Rights and Privacy Act


class ComplianceStatus(Enum):
    """Status of a compliance check."""
    COMPLIANT = "compliant"  # Fully compliant
    NON_COMPLIANT = "non_compliant"  # Not compliant
    PARTIAL = "partial"  # Partially compliant
    NOT_APPLICABLE = "not_applicable"  # Framework not applicable
    PENDING = "pending"  # Compliance check pending
    WAIVED = "waived"  # Compliance requirement waived


class ComplianceRequirement(Enum):
    """Common compliance requirements across frameworks."""
    DATA_PRIVACY = "data_privacy"  # Protect personal data
    DATA_RETENTION = "data_retention"  # Proper data retention policies
    ACCESS_CONTROL = "access_control"  # Control who can access data
    AUDIT_TRAIL = "audit_trail"  # Maintain audit trails
    ENCRYPTION = "encryption"  # Encrypt sensitive data
    CONSENT = "consent"  # Obtain user consent
    RIGHT_TO_ERASURE = "right_to_erasure"  # Allow data deletion
    DATA_PORTABILITY = "data_portability"  # Allow data export
    BREACH_NOTIFICATION = "breach_notification"  # Notify of breaches
    RISK_ASSESSMENT = "risk_assessment"  # Conduct risk assessments
    INCIDENT_RESPONSE = "incident_response"  # Have incident response plan
    VENDOR_MANAGEMENT = "vendor_management"  # Manage third-party vendors


@dataclass(frozen=True)
class ComplianceCheck:
    """A compliance check for a specific framework and requirement.
    
    Attributes:
        check_id: Unique identifier for this check
        framework: Regulatory framework being checked
        requirement: Specific requirement being validated
        description: Description of what is being checked
        severity: Severity if check fails
        mandatory: Whether this check is mandatory
        can_waive: Whether this check can be waived
        waive_requires_authority: Authority level required to waive
        validation_function: Function to execute for validation
        metadata: Additional check metadata
    """
    check_id: str
    framework: RegulatoryFramework
    requirement: ComplianceRequirement
    description: str
    severity: DecisionSeverity
    mandatory: bool
    can_waive: bool
    waive_requires_authority: Optional[DecisionSeverity]
    validation_function: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate compliance check."""
        if not self.check_id:
            raise ValueError("check_id cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")
        if not self.validation_function:
            raise ValueError("validation_function cannot be empty")
        
        # Mandatory checks cannot be waived
        if self.mandatory and self.can_waive:
            raise ValueError("Mandatory checks cannot be waived")
        
        # If can waive, must specify required authority
        if self.can_waive and self.waive_requires_authority is None:
            raise ValueError("Waivable check must specify waive_requires_authority")


@dataclass(frozen=True)
class ComplianceCheckResult:
    """Result of a compliance check.
    
    Attributes:
        check: The compliance check that was performed
        status: Status of the compliance check
        checked_at: When the check was performed
        checked_by: Who/what performed the check
        compliant: Whether the check passed (convenience field)
        violation_details: Details of any violations found
        remediation_steps: Steps to remediate violations
        waive_reason: Reason for waiving (if waived)
        waive_authority: Authority that approved waiver
        metadata: Additional result metadata
    """
    check: ComplianceCheck
    status: ComplianceStatus
    checked_at: datetime
    checked_by: str
    compliant: bool
    violation_details: Optional[str] = None
    remediation_steps: List[str] = field(default_factory=list)
    waive_reason: Optional[str] = None
    waive_authority: Optional[DecisionAuthority] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate compliance check result."""
        # If non-compliant, must have violation details
        if self.status == ComplianceStatus.NON_COMPLIANT and not self.violation_details:
            raise ValueError("Non-compliant check must have violation_details")
        
        # If waived, must have waive_reason and waive_authority
        if self.status == ComplianceStatus.WAIVED:
            if not self.waive_reason:
                raise ValueError("Waived check must have waive_reason")
            if not self.waive_authority:
                raise ValueError("Waived check must have waive_authority")
        
        # compliant field must match status
        expected_compliant = self.status in (
            ComplianceStatus.COMPLIANT,
            ComplianceStatus.WAIVED,
            ComplianceStatus.NOT_APPLICABLE
        )
        if self.compliant != expected_compliant:
            raise ValueError(f"compliant={self.compliant} inconsistent with status={self.status}")


@dataclass(frozen=True)
class ComplianceContext:
    """Context for compliance checks.
    
    Attributes:
        frameworks: Frameworks to check compliance against
        decision_severity: Severity of the decision
        authority: Authority executing the decision
        ownership: Ownership chain
        involves_personal_data: Whether decision involves personal data
        involves_financial_data: Whether decision involves financial data
        involves_health_data: Whether decision involves health data
        data_subjects: Number of data subjects affected
        geographic_scope: Geographic regions affected
        metadata: Additional context metadata
    """
    frameworks: Set[RegulatoryFramework]
    decision_severity: DecisionSeverity
    authority: DecisionAuthority
    ownership: AccountabilityChain
    involves_personal_data: bool
    involves_financial_data: bool
    involves_health_data: bool
    data_subjects: int = 0
    geographic_scope: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate compliance context."""
        if not self.frameworks:
            raise ValueError("At least one framework must be specified")
        if self.data_subjects < 0:
            raise ValueError("data_subjects cannot be negative")


# Predefined Compliance Checks

GDPR_DATA_PRIVACY_CHECK = ComplianceCheck(
    check_id="gdpr_data_privacy",
    framework=RegulatoryFramework.GDPR,
    requirement=ComplianceRequirement.DATA_PRIVACY,
    description="Ensure personal data is processed lawfully and transparently",
    severity=DecisionSeverity.CRITICAL,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_gdpr_data_privacy",
    metadata={"article": "Article 5", "principle": "Lawfulness, fairness and transparency"}
)

GDPR_CONSENT_CHECK = ComplianceCheck(
    check_id="gdpr_consent",
    framework=RegulatoryFramework.GDPR,
    requirement=ComplianceRequirement.CONSENT,
    description="Verify valid consent obtained for data processing",
    severity=DecisionSeverity.CRITICAL,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_gdpr_consent",
    metadata={"article": "Article 7", "principle": "Conditions for consent"}
)

GDPR_AUDIT_TRAIL_CHECK = ComplianceCheck(
    check_id="gdpr_audit_trail",
    framework=RegulatoryFramework.GDPR,
    requirement=ComplianceRequirement.AUDIT_TRAIL,
    description="Maintain complete audit trail of data processing activities",
    severity=DecisionSeverity.ELEVATED,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_gdpr_audit_trail",
    metadata={"article": "Article 30", "principle": "Records of processing activities"}
)

SOC2_ACCESS_CONTROL_CHECK = ComplianceCheck(
    check_id="soc2_access_control",
    framework=RegulatoryFramework.SOC2,
    requirement=ComplianceRequirement.ACCESS_CONTROL,
    description="Verify proper access controls are in place",
    severity=DecisionSeverity.ELEVATED,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_soc2_access_control",
    metadata={"trust_principle": "Security", "category": "Access Control"}
)

SOC2_AUDIT_TRAIL_CHECK = ComplianceCheck(
    check_id="soc2_audit_trail",
    framework=RegulatoryFramework.SOC2,
    requirement=ComplianceRequirement.AUDIT_TRAIL,
    description="Maintain audit logs for all system activities",
    severity=DecisionSeverity.ELEVATED,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_soc2_audit_trail",
    metadata={"trust_principle": "Security", "category": "Monitoring"}
)

ISO27001_RISK_ASSESSMENT_CHECK = ComplianceCheck(
    check_id="iso27001_risk_assessment",
    framework=RegulatoryFramework.ISO27001,
    requirement=ComplianceRequirement.RISK_ASSESSMENT,
    description="Conduct risk assessment for information security",
    severity=DecisionSeverity.ELEVATED,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_iso27001_risk_assessment",
    metadata={"control": "A.12.6", "category": "Technical vulnerability management"}
)

PCI_DSS_ENCRYPTION_CHECK = ComplianceCheck(
    check_id="pci_dss_encryption",
    framework=RegulatoryFramework.PCI_DSS,
    requirement=ComplianceRequirement.ENCRYPTION,
    description="Encrypt cardholder data in transit and at rest",
    severity=DecisionSeverity.CRITICAL,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_pci_dss_encryption",
    metadata={"requirement": "3.4", "category": "Protect Cardholder Data"}
)

PCI_DSS_ACCESS_CONTROL_CHECK = ComplianceCheck(
    check_id="pci_dss_access_control",
    framework=RegulatoryFramework.PCI_DSS,
    requirement=ComplianceRequirement.ACCESS_CONTROL,
    description="Restrict access to cardholder data by business need-to-know",
    severity=DecisionSeverity.CRITICAL,
    mandatory=True,
    can_waive=False,
    waive_requires_authority=None,
    validation_function="validate_pci_dss_access_control",
    metadata={"requirement": "7.1", "category": "Restrict Access"}
)

# Compliance Check Collections

GDPR_CHECKS = [
    GDPR_DATA_PRIVACY_CHECK,
    GDPR_CONSENT_CHECK,
    GDPR_AUDIT_TRAIL_CHECK,
]

SOC2_CHECKS = [
    SOC2_ACCESS_CONTROL_CHECK,
    SOC2_AUDIT_TRAIL_CHECK,
]

ISO27001_CHECKS = [
    ISO27001_RISK_ASSESSMENT_CHECK,
]

PCI_DSS_CHECKS = [
    PCI_DSS_ENCRYPTION_CHECK,
    PCI_DSS_ACCESS_CONTROL_CHECK,
]

ALL_COMPLIANCE_CHECKS = (
    GDPR_CHECKS +
    SOC2_CHECKS +
    ISO27001_CHECKS +
    PCI_DSS_CHECKS
)


def get_applicable_checks(
    frameworks: Set[RegulatoryFramework],
    context: ComplianceContext
) -> List[ComplianceCheck]:
    """Get applicable compliance checks for given frameworks and context.
    
    Args:
        frameworks: Regulatory frameworks to check
        context: Compliance context
    
    Returns:
        List of applicable compliance checks
    """
    applicable = []
    
    for check in ALL_COMPLIANCE_CHECKS:
        if check.framework not in frameworks:
            continue
        
        # Filter based on data types
        if check.requirement == ComplianceRequirement.DATA_PRIVACY:
            if not context.involves_personal_data:
                continue
        
        if check.framework == RegulatoryFramework.PCI_DSS:
            if not context.involves_financial_data:
                continue
        
        if check.framework == RegulatoryFramework.HIPAA:
            if not context.involves_health_data:
                continue
        
        applicable.append(check)
    
    return applicable


def check_compliance(
    context: ComplianceContext,
    checks: Optional[List[ComplianceCheck]] = None
) -> List[ComplianceCheckResult]:
    """Perform compliance checks.
    
    Args:
        context: Compliance context
        checks: Specific checks to perform (or None for all applicable)
    
    Returns:
        List of compliance check results
    """
    if checks is None:
        checks = get_applicable_checks(context.frameworks, context)
    
    results = []
    
    for check in checks:
        # For now, create placeholder results
        # In production, this would call actual validation functions
        result = ComplianceCheckResult(
            check=check,
            status=ComplianceStatus.PENDING,
            checked_at=datetime.utcnow(),
            checked_by="compliance_engine",
            compliant=False,
            violation_details=None,
            remediation_steps=[],
            metadata={"note": "Validation function not yet implemented"}
        )
        results.append(result)
    
    return results


def is_compliant(
    results: List[ComplianceCheckResult],
    allow_partial: bool = False
) -> bool:
    """Check if all compliance checks passed.
    
    Args:
        results: Compliance check results
        allow_partial: Whether to allow partial compliance
    
    Returns:
        True if compliant, False otherwise
    """
    if not results:
        return True
    
    for result in results:
        if result.status == ComplianceStatus.NON_COMPLIANT:
            return False
        if result.status == ComplianceStatus.PARTIAL and not allow_partial:
            return False
    
    return True


def get_compliance_violations(
    results: List[ComplianceCheckResult]
) -> List[ComplianceCheckResult]:
    """Get all compliance violations from results.
    
    Args:
        results: Compliance check results
    
    Returns:
        List of results with violations
    """
    return [
        result for result in results
        if result.status in (ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIAL)
    ]


def can_waive_check(
    check: ComplianceCheck,
    authority: DecisionAuthority
) -> bool:
    """Check if an authority can waive a compliance check.
    
    Args:
        check: Compliance check to waive
        authority: Authority attempting to waive
    
    Returns:
        True if authority can waive, False otherwise
    """
    if not check.can_waive:
        return False
    
    if check.waive_requires_authority is None:
        return False
    
    # Check if authority's max severity >= required waive severity
    severity_order = [
        DecisionSeverity.ROUTINE,
        DecisionSeverity.ELEVATED,
        DecisionSeverity.CRITICAL,
        DecisionSeverity.EMERGENCY,
        DecisionSeverity.CATASTROPHIC,
    ]
    
    authority_level = severity_order.index(authority.max_decision_severity)
    required_level = severity_order.index(check.waive_requires_authority)
    
    return authority_level >= required_level