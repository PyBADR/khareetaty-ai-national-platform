# Decision Engine

## Overview

The Decision Engine is the core orchestration service for all decision-making activities in the BDR Insurance Platform. It provides a unified interface for executing decisions, managing decision lifecycle, and ensuring proper governance.

## Key Components

### DecisionOrchestrator

Main entry point for all decisions. Coordinates:
- Input validation
- Policy enforcement
- Decision execution
- Approval routing
- Audit logging
- Telemetry

### Decision Types

1. **ADVISORY**: System provides recommendations, human makes final decision
2. **BOUNDED**: Automated within defined constraints, escalates exceptions
3. **SIMULATION**: What-if analysis, no real-world impact

## Usage Example

```python
from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext

# Initialize orchestrator
orchestrator = DecisionOrchestrator(
    policy_engine=policy_engine,
    audit_logger=audit_logger,
    telemetry=telemetry
)

# Create context
context = DecisionContext(
    user_id="adjuster@example.com",
    user_role="adjuster"
)

# Execute decision
result = orchestrator.execute_decision(
    decision_type=DecisionType.ADVISORY,
    input_data={"claim_id": "CLM-001", "severity": 6},
    context=context,
    module_name="fnol_triage"
)

# Check result
if result.requires_approval:
    print(f"Approval required at level {result.approval_level}")
else:
    print(f"Decision: {result.recommendation} (confidence: {result.confidence})")
```

## Architecture

```
Module Service
    ↓
DecisionOrchestrator
    ↓
├── Input Validation
├── Policy Check
├── Decision Logic (delegated to module)
├── Approval Determination
├── Audit Logging
└── Telemetry
```

## Integration Points

- **Policy Engine**: Validates decisions against policies
- **Audit Logger**: Records all decisions
- **Telemetry**: Tracks performance metrics
- **Governance**: Routes approvals

## Configuration

No configuration required - orchestrator is stateless and receives dependencies via constructor injection.

## Testing

```bash
pytest core/decision_engine/tests/
```

## Extending

To add new decision types:
1. Add to `DecisionType` enum
2. Update approval logic in orchestrator
3. Document decision type behavior
4. Add tests

## Best Practices

1. Always provide complete context
2. Use appropriate decision type
3. Handle approval requirements
4. Log all decisions
5. Monitor confidence scores
