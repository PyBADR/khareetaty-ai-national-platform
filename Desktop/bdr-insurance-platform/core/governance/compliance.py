"""
Compliance Checker

Extracted from: insurance-hf-project/create_gradio_space.py
Purpose: Enforce compliance rules and regulatory requirements
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ComplianceRuleType(str, Enum):
    """Type of compliance rule"""
    REGULATORY = "regulatory"  # Government/regulatory requirement
    BUSINESS = "business"  # Internal business policy
    ETHICAL = "ethical"  # Ethical guidelines
    OPERATIONAL = "operational"  # Operational standards


class ComplianceSeverity(str, Enum):
    """Severity of compliance violation"""
    CRITICAL = "critical"  # Must be fixed, blocks processing
    HIGH = "high"  # Should be fixed, allows processing with warning
    MEDIUM = "medium"  # Should be addressed
    LOW = "low"  # Nice to fix
    INFO = "info"  # Informational only


@dataclass
class ComplianceRule:
    """Defines a compliance rule"""
    rule_id: str
    name: str
    description: str
    rule_type: ComplianceRuleType
    severity: ComplianceSeverity
    check_function: Callable[[Dict[str, Any]], bool]
    remediation: str  # How to fix violations
    references: List[str] = None  # Regulatory references
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class ComplianceViolation:
    """Record of a compliance violation"""
    rule: ComplianceRule
    timestamp: datetime
    context: Dict[str, Any]
    message: str
    
    @property
    def is_blocking(self) -> bool:
        """Whether this violation blocks processing"""
        return self.rule.severity == ComplianceSeverity.CRITICAL


@dataclass
class ComplianceReport:
    """Report of compliance check results"""
    timestamp: datetime
    is_compliant: bool
    violations: List[ComplianceViolation]
    warnings: List[str]
    passed_rules: List[str]
    
    @property
    def has_blocking_violations(self) -> bool:
        """Whether report contains blocking violations"""
        return any(v.is_blocking for v in self.violations)
    
    def format_report(self) -> str:
        """Format compliance report as human-readable text"""
        report = "\n## ⚖️ Compliance Report\n\n"
        report += f"**Timestamp**: {self.timestamp.isoformat()}\n"
        report += f"**Status**: {'✅ COMPLIANT' if self.is_compliant else '❌ NON-COMPLIANT'}\n\n"
        
        if self.violations:
            report += f"### Violations ({len(self.violations)})\n\n"
            for v in self.violations:
                icon = "🚨" if v.is_blocking else "⚠️"
                report += f"{icon} **{v.rule.name}** ({v.rule.severity.value})\n"
                report += f"   - {v.message}\n"
                report += f"   - **Remediation**: {v.rule.remediation}\n\n"
        
        if self.warnings:
            report += f"### Warnings ({len(self.warnings)})\n\n"
            for warning in self.warnings:
                report += f"⚠️ {warning}\n"
            report += "\n"
        
        if self.passed_rules:
            report += f"### Passed Rules ({len(self.passed_rules)})\n\n"
            for rule in self.passed_rules:
                report += f"✅ {rule}\n"
        
        return report


class ComplianceChecker:
    """
    Checks compliance with regulatory and business rules.
    
    Ensures all decision-making processes adhere to:
    - Fair Claims Settlement Practices
    - Explainable AI Standards
    - Data Protection Regulations
    - Insurance Regulatory Requirements
    """
    
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register default compliance rules"""
        
        # Human oversight requirement
        self.register_rule(ComplianceRule(
            rule_id="HUMAN_OVERSIGHT_001",
            name="Human Decision Authority",
            description="All decisions must have human oversight and approval",
            rule_type=ComplianceRuleType.REGULATORY,
            severity=ComplianceSeverity.CRITICAL,
            check_function=lambda ctx: ctx.get('human_approved', False),
            remediation="Ensure human reviewer approves the decision",
            references=["Fair Claims Settlement Practices", "AI Governance Standards"]
        ))
        
        # Justification requirement
        self.register_rule(ComplianceRule(
            rule_id="JUSTIFICATION_001",
            name="Decision Justification Required",
            description="Human decisions must include written justification",
            rule_type=ComplianceRuleType.REGULATORY,
            severity=ComplianceSeverity.CRITICAL,
            check_function=lambda ctx: bool(ctx.get('justification', '').strip()),
            remediation="Provide written justification for the decision",
            references=["Audit Requirements", "Explainable AI Standards"]
        ))
        
        # Audit trail requirement
        self.register_rule(ComplianceRule(
            rule_id="AUDIT_001",
            name="Audit Trail Completeness",
            description="All decisions must be logged with complete audit trail",
            rule_type=ComplianceRuleType.REGULATORY,
            severity=ComplianceSeverity.CRITICAL,
            check_function=lambda ctx: all([
                ctx.get('decision_id'),
                ctx.get('timestamp'),
                ctx.get('decision_maker')
            ]),
            remediation="Ensure decision ID, timestamp, and decision maker are recorded",
            references=["Audit Standards", "Record Retention Requirements"]
        ))
        
        # Explainability requirement
        self.register_rule(ComplianceRule(
            rule_id="EXPLAIN_001",
            name="Decision Explainability",
            description="AI recommendations must include explanation of reasoning",
            rule_type=ComplianceRuleType.REGULATORY,
            severity=ComplianceSeverity.HIGH,
            check_function=lambda ctx: bool(ctx.get('explanation') or ctx.get('reasoning')),
            remediation="Provide explanation of AI reasoning and key factors",
            references=["Explainable AI Standards", "Fair Lending Practices"]
        ))
        
        # Uncertainty disclosure
        self.register_rule(ComplianceRule(
            rule_id="UNCERTAINTY_001",
            name="Uncertainty Disclosure",
            description="High uncertainty must be disclosed to decision makers",
            rule_type=ComplianceRuleType.ETHICAL,
            severity=ComplianceSeverity.HIGH,
            check_function=lambda ctx: (
                not ctx.get('uncertainty_flag', False) or 
                ctx.get('uncertainty_disclosed', False)
            ),
            remediation="Disclose uncertainty to human decision maker",
            references=["Ethical AI Guidelines", "Transparency Standards"]
        ))
        
        # No autonomous decisions
        self.register_rule(ComplianceRule(
            rule_id="AUTONOMY_001",
            name="No Autonomous Decisions",
            description="System must not make autonomous decisions without human approval",
            rule_type=ComplianceRuleType.REGULATORY,
            severity=ComplianceSeverity.CRITICAL,
            check_function=lambda ctx: ctx.get('decision_mode') != 'autonomous',
            remediation="Ensure decision mode is 'advisory' or 'human-in-loop'",
            references=["AI Governance", "Insurance Regulations"]
        ))
    
    def register_rule(self, rule: ComplianceRule):
        """Register a compliance rule"""
        self.rules[rule.rule_id] = rule
    
    def check_compliance(self, context: Dict[str, Any]) -> ComplianceReport:
        """
        Check compliance against all registered rules.
        
        Args:
            context: Decision context to check
        
        Returns:
            ComplianceReport with results
        """
        violations = []
        warnings = []
        passed_rules = []
        
        for rule_id, rule in self.rules.items():
            try:
                is_compliant = rule.check_function(context)
                
                if is_compliant:
                    passed_rules.append(rule.name)
                else:
                    violation = ComplianceViolation(
                        rule=rule,
                        timestamp=datetime.now(),
                        context=context,
                        message=f"Violation of {rule.name}: {rule.description}"
                    )
                    violations.append(violation)
                    
            except Exception as e:
                warnings.append(f"Error checking rule {rule_id}: {str(e)}")
        
        return ComplianceReport(
            timestamp=datetime.now(),
            is_compliant=len(violations) == 0,
            violations=violations,
            warnings=warnings,
            passed_rules=passed_rules
        )
    
    def check_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        """
        Check a specific compliance rule.
        
        Args:
            rule_id: ID of the rule to check
            context: Decision context
        
        Returns:
            True if compliant, False otherwise
        """
        if rule_id not in self.rules:
            raise ValueError(f"Unknown rule ID: {rule_id}")
        
        rule = self.rules[rule_id]
        return rule.check_function(context)
    
    def get_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """Get a compliance rule by ID"""
        return self.rules.get(rule_id)
    
    def list_rules(self, rule_type: Optional[ComplianceRuleType] = None) -> List[ComplianceRule]:
        """
        List all compliance rules, optionally filtered by type.
        
        Args:
            rule_type: Optional filter by rule type
        
        Returns:
            List of compliance rules
        """
        rules = list(self.rules.values())
        
        if rule_type:
            rules = [r for r in rules if r.rule_type == rule_type]
        
        return rules
