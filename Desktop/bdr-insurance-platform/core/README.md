# Core Platform Layer

## Overview

The `core/` directory contains the foundational platform services that ALL business modules must use. These services provide:

- **Decision orchestration** - Standardized decision workflows
- **Policy enforcement** - Business rules and regulatory compliance
- **Audit logging** - Complete audit trail for all decisions
- **Telemetry** - Performance monitoring and observability
- **Security** - Authentication, authorization, and access control
- **Governance** - Human-in-the-loop controls and validation

## Architecture Principles

### 1. **No Hugging Face Dependencies**
Core services are platform-agnostic and contain NO references to:
- Hugging Face libraries
- Model-specific code
- UI frameworks

### 2. **Deterministic & Testable**
All core services must be:
- Fully unit testable
- Deterministic (same input → same output)
- Free of side effects where possible

### 3. **Domain-Agnostic**
Core services should work for ANY insurance decision type:
- FNOL triage
- Fraud detection
- IFRS accrual
- Underwriting
- Reinsurance

### 4. **Explicit Boundaries**
Each core module has:
- Clear public API (exported via `__init__.py`)
- Documented interfaces
- Forbidden cross-coupling

## Module Structure

```
core/
├── __init__.py              # Core platform exports
├── README.md                # This file
│
├── decision_engine/         # Decision orchestration
│   ├── __init__.py
│   ├── models.py           # DecisionType, DecisionContext, DecisionResult
│   ├── orchestrator.py     # Main decision workflow coordinator
│   └── README.md
│
├── policy_engine/           # Policy enforcement
│   ├── __init__.py
│   ├── models.py           # Policy, Constraint, ValidationResult
│   ├── enforcer.py         # Policy validation logic
│   └── README.md
│
├── audit_logging/           # Audit trail
│   ├── __init__.py
│   ├── logger.py           # AuditLogger, AuditEntry
│   ├── storage.py          # Audit storage backends
│   └── README.md
│
├── telemetry/               # Observability
│   ├── __init__.py
│   ├── collector.py        # Metrics collection
│   ├── metrics.py          # Metric types (Counter, Gauge, etc.)
│   └── README.md
│
├── security/                # Access control
│   ├── __init__.py
│   ├── auth.py             # Authentication
│   ├── authz.py            # Authorization (RBAC)
│   ├── access_control.py   # Fine-grained ACLs
│   └── README.md
│
└── governance/              # Human-in-the-loop
    ├── __init__.py
    ├── validators.py       # Input validation
    ├── human_oversight.py  # Approval workflows
    ├── compliance.py       # Compliance checks
    └── README.md
```

## Import Rules

### ✅ ALLOWED

```python
# Business modules importing from core
from core.decision_engine import DecisionOrchestrator, DecisionType
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
```

### ❌ FORBIDDEN

```python
# Core importing from modules (NEVER)
from modules.fnol_triage import FNOLEngine  # ❌ WRONG

# Core importing Hugging Face (NEVER)
from transformers import AutoModel  # ❌ WRONG

# Core importing UI frameworks (NEVER)
import gradio as gr  # ❌ WRONG
```

## Decision Engine

### Purpose
Orchestrates all decision workflows across the platform.

### Key Components

**DecisionType** (Enum)
- `ADVISORY` - System recommends, human decides
- `BOUNDED` - Automated within constraints, escalates exceptions
- `SIMULATION` - What-if analysis, no real-world impact

**DecisionContext**
- User identity and role
- Trace ID for distributed tracing
- Session metadata
- Timestamp

**DecisionResult**
- Recommendation
- Confidence score (0.0 - 1.0)
- Reasoning (explainability)
- Alternatives
- Approval requirements

**DecisionOrchestrator**
- Main entry point for all decisions
- Coordinates policy checks, audit logging, telemetry
- Determines approval requirements
- Manages decision lifecycle

### Usage Example

```python
from core.decision_engine import (
    DecisionOrchestrator,
    DecisionType,
    DecisionContext
)

# Initialize orchestrator
orchestrator = DecisionOrchestrator(
    policy_engine=policy_enforcer,
    audit_logger=audit_logger,
    telemetry=telemetry_collector
)

# Create context
context = DecisionContext(
    user_id="adjuster@example.com",
    user_role="adjuster",
    session_id="sess_123"
)

# Execute decision
result = orchestrator.execute_decision(
    decision_type=DecisionType.ADVISORY,
    input_data={"claim_id": "CLM-001", "severity": 7},
    context=context,
    module_name="fnol_triage"
)

print(f"Recommendation: {result.recommendation}")
print(f"Confidence: {result.confidence}")
print(f"Requires approval: {result.requires_approval}")
```

## Policy Engine

### Purpose
Enforces business rules, constraints, and regulatory requirements.

### Key Components

**PolicyType** (Enum)
- `REGULATORY` - Compliance requirements (hard failures)
- `BUSINESS` - Business rules (warnings)
- `OPERATIONAL` - SLAs, performance (warnings)

**Policy**
- Policy ID and name
- Policy type
- Rules (dict of conditions)
- Priority (for conflict resolution)

**PolicyEnforcer**
- Validates decisions against policies
- Returns violations and warnings
- Supports policy hierarchy

### Usage Example

```python
from core.policy_engine import PolicyEnforcer, Policy, PolicyType

# Define a policy
policy = Policy(
    policy_id="min_confidence",
    name="Minimum Confidence Threshold",
    description="Decisions must have confidence >= 0.85",
    policy_type=PolicyType.BUSINESS,
    rules={"min_confidence": 0.85},
    priority=10
)

# Create enforcer
enforcer = PolicyEnforcer(policies=[policy])

# Validate decision
validation = enforcer.validate_decision(decision)

if not validation.is_valid:
    print(f"Violations: {validation.violations}")
```

## Audit Logging

### Purpose
Provides complete audit trail for all decision-making processes.

### Key Components

**AuditLogger**
- Logs all decisions with full context
- Supports multiple storage backends
- Immutable audit records

**AuditEntry**
- Timestamp
- User identity
- Action performed
- Input/output data
- Decision outcome

### Usage Example

```python
from core.audit_logging import AuditLogger, AuditLevel

audit_logger = AuditLogger()

audit_logger.log_decision(
    decision=decision,
    context=context,
    result=result
)
```

## Security

### Purpose
Provides authentication, authorization, and access control.

### Key Components

**AuthenticationManager**
- User authentication
- Token management
- Session handling

**AuthorizationManager**
- Role-based access control (RBAC)
- Permission checking
- Default role hierarchy:
  - Adjuster
  - Fraud Analyst
  - Underwriter
  - Manager
  - Administrator

**AccessControlList**
- Fine-grained resource access
- User and role-based policies
- Access levels: NONE, READ, WRITE, ADMIN

### Usage Example

```python
from core.security import (
    AuthenticationManager,
    AuthorizationManager,
    Permission
)

# Authenticate user
auth_mgr = AuthenticationManager()
token = auth_mgr.authenticate("user@example.com", "password")

# Check permissions
authz_mgr = AuthorizationManager()
authz_mgr.assign_role(user_id, "adjuster")

if authz_mgr.check_permission(user_id, Permission.DECISION_CREATE):
    # User can create decisions
    pass
```

## Telemetry

### Purpose
Provides metrics collection, performance monitoring, and observability.

### Key Components

**TelemetryCollector**
- Collects metrics from all platform operations
- Supports multiple metric types
- Exportable to monitoring systems

**Metric Types**
- Counter - Monotonically increasing values
- Gauge - Point-in-time values
- Histogram - Distribution of values
- Timer - Duration measurements

### Usage Example

```python
from core.telemetry import TelemetryCollector, Counter

telemetry = TelemetryCollector()

telemetry.record_decision(
    decision_type="advisory",
    confidence=0.87,
    module="fnol_triage"
)
```

## Governance

### Purpose
Provides human-in-the-loop controls, validation, and compliance enforcement.

### Key Components

**HumanOversightManager**
- Manages approval workflows
- Determines oversight level required
- Tracks approval status

**InputValidator**
- Validates input data
- Checks data quality
- Enforces schema compliance

**ComplianceChecker**
- Verifies regulatory compliance
- Checks against compliance rules
- Generates compliance reports

## Testing Core Services

All core services MUST have comprehensive unit tests:

```bash
# Run core tests
pytest core/tests/

# Run with coverage
pytest core/tests/ --cov=core --cov-report=html
```

## Extension Points

Core services are designed to be extended:

1. **Custom Policy Rules** - Add new policy types and rule evaluators
2. **Audit Storage Backends** - Implement custom storage (database, S3, etc.)
3. **Telemetry Exporters** - Export to Prometheus, DataDog, etc.
4. **Authentication Providers** - Integrate with SSO, SAML, OAuth

## Migration Notes

When migrating logic from Hugging Face Spaces:

1. ✅ Extract business logic → move to `modules/`
2. ✅ Extract governance rules → move to `core/policy_engine`
3. ✅ Extract validation logic → move to `core/governance`
4. ❌ DO NOT move UI code to core
5. ❌ DO NOT move model-specific code to core

## TODO Markers

Core services use structured TODO markers:

```python
# TODO(platform): Implement distributed tracing integration
# FIXME(security): Replace placeholder auth with SSO
# NOTE(governance): This threshold is configurable per deployment
```

## Version History

- **v1.0.0** (2026-01-20) - Initial core platform implementation
