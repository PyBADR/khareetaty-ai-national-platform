# Governance Module

## Overview

The Governance module provides human-in-the-loop controls, validation, and compliance enforcement for all decision-making processes in the BDR Insurance Platform.

**Source**: Extracted from `insurance-hf-project/create_gradio_space.py`

## Key Principles

1. **Human Authority**: Humans have final decision authority
2. **No Automation**: NO automatic approvals or rejections
3. **Mandatory Justification**: All decisions require human justification
4. **Full Auditability**: Complete audit trail for all decisions
5. **Compliance First**: Regulatory compliance is non-negotiable

## Components

### 1. Validators (`validators.py`)

**InputValidator**
- Validates input data quality and completeness
- Checks required fields, numeric ranges, data types
- Provides warnings for missing documentation or high-value claims

**JustificationValidator**
- Enforces human justification requirements
- Validates minimum/maximum length
- Detects generic or template responses
- Context-aware validation for high-risk decisions

### 2. Human Oversight (`human_oversight.py`)

**OversightLevel** (Enum)
- `NONE`: No human review needed (rare)
- `ADVISORY`: Human reviews but system can proceed
- `REQUIRED`: Human must approve before proceeding
- `MANDATORY`: Human must approve + provide justification
- `ESCALATION`: Must escalate to senior authority

**HumanOversightManager**
- Determines required oversight level based on risk, confidence, uncertainty
- Validates oversight completion
- Records all oversight actions
- Formats oversight notices for humans

**Key Features**:
- Automatic escalation for high-risk decisions (risk_score >= 80)
- Automatic escalation for high uncertainty (confidence < 0.6)
- Additional oversight for high-value claims (> $50,000)
- Tracks all oversight records for audit

### 3. Compliance (`compliance.py`)

**ComplianceChecker**
- Enforces regulatory and business rules
- Validates compliance before processing
- Generates compliance reports

**Default Compliance Rules**:

| Rule ID | Name | Severity | Description |
|---------|------|----------|-------------|
| `HUMAN_OVERSIGHT_001` | Human Decision Authority | CRITICAL | All decisions must have human oversight |
| `JUSTIFICATION_001` | Decision Justification Required | CRITICAL | Human decisions must include written justification |
| `AUDIT_001` | Audit Trail Completeness | CRITICAL | All decisions must be logged with complete audit trail |
| `EXPLAIN_001` | Decision Explainability | HIGH | AI recommendations must include explanation |
| `UNCERTAINTY_001` | Uncertainty Disclosure | HIGH | High uncertainty must be disclosed |
| `AUTONOMY_001` | No Autonomous Decisions | CRITICAL | System must not make autonomous decisions |

## Usage Examples

### Example 1: Validate Input

```python
from core.governance import InputValidator

validator = InputValidator()
result = validator.validate_claim_input(
    claim_id="CLM-12345",
    claim_amount=75000,
    documentation_complete=False,
    has_police_report=False
)

if not result.is_valid:
    print("Errors:", result.errors)
if result.warnings:
    print("Warnings:", result.warnings)
```

### Example 2: Determine Oversight Level

```python
from core.governance import HumanOversightManager

manager = HumanOversightManager()
requirement = manager.determine_oversight_level(
    risk_score=85,
    confidence=0.72,
    uncertainty_flag=False,
    amount=100000
)

print(f"Oversight Level: {requirement.level}")
print(f"Escalation Reason: {requirement.escalation_reason}")
print(f"Min Justification Length: {requirement.min_justification_length}")
```

### Example 3: Check Compliance

```python
from core.governance import ComplianceChecker

checker = ComplianceChecker()
report = checker.check_compliance({
    'human_approved': True,
    'justification': 'Claim approved based on complete documentation...',
    'decision_id': 'DEC-12345',
    'timestamp': '2026-01-20T10:30:00',
    'decision_maker': 'adjuster_001',
    'explanation': 'Risk score is low, all evidence present',
    'uncertainty_flag': False,
    'decision_mode': 'human-in-loop'
})

if report.is_compliant:
    print("✅ All compliance checks passed")
else:
    print(report.format_report())
```

### Example 4: Validate Justification

```python
from core.governance import JustificationValidator

validator = JustificationValidator(min_length=50)
result = validator.validate_with_context(
    justification="After reviewing all evidence and documentation, I approve this claim because...",
    decision_context={
        'risk_level': 'HIGH',
        'uncertainty_flag': True
    }
)

if result.is_valid:
    print("✅ Justification is valid")
else:
    print("Errors:", result.errors)
```

## Integration with Decision Engine

The Governance module integrates with `core/decision_engine/orchestrator.py`:

```python
from core.decision_engine import DecisionOrchestrator
from core.governance import HumanOversightManager, ComplianceChecker

orchestrator = DecisionOrchestrator(
    policy_engine=policy_engine,
    audit_logger=audit_logger,
    telemetry=telemetry
)

# Governance is enforced during decision execution
result = orchestrator.execute_decision(
    decision_type=DecisionType.ADVISORY,
    context=context,
    input_data=input_data
)
```

## Regulatory References

- **Fair Claims Settlement Practices**: State insurance regulations
- **Explainable AI Standards**: NIST AI Risk Management Framework
- **Data Protection Regulations**: GDPR, CCPA
- **Insurance Regulatory Requirements**: State DOI regulations
- **Audit Standards**: SOC 2, ISO 27001

## Design Decisions

### Why Mandatory Human Oversight?

Insurance decisions have significant financial and personal impact. Regulatory requirements and ethical considerations mandate human oversight for:
- Claims approval/denial
- Fraud detection
- Underwriting decisions
- Pricing adjustments

### Why Justification is Required?

Written justification ensures:
- **Accountability**: Decision makers are accountable
- **Auditability**: Decisions can be reviewed and audited
- **Quality**: Forces thoughtful decision-making
- **Compliance**: Meets regulatory documentation requirements

### Why Escalation Rules?

Automatic escalation for high-risk/high-uncertainty cases ensures:
- **Risk Management**: Senior review for critical decisions
- **Quality Control**: Additional oversight for complex cases
- **Compliance**: Meets regulatory requirements for high-value claims

## Testing

See `tests/core/governance/` for comprehensive test suite.

## TODO

- [ ] Add integration with external audit systems
- [ ] Implement role-based access control (RBAC)
- [ ] Add support for multi-level approval workflows
- [ ] Create compliance rule templates for different jurisdictions
- [ ] Add automated compliance reporting

## Changelog

### v1.0.0 (2026-01-20)
- Initial extraction from insurance-hf-project
- Implemented InputValidator, JustificationValidator
- Implemented HumanOversightManager with 5 oversight levels
- Implemented ComplianceChecker with 6 default rules
- Full documentation and usage examples
