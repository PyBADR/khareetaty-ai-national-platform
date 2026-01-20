# Core Module Boundaries and Import Rules

## Purpose

This document defines the **strict boundaries** between core platform services and establishes **non-negotiable import rules** that prevent coupling and maintain architectural integrity.

## Architectural Layers

```
┌──────────────────────────────────────────────────┐
│  Hugging Face Spaces (UI Layer)                      │
│  - Gradio interfaces                                  │
│  - Streamlit apps                                     │
│  - Demo shells                                        │
└──────────────────────────────────────────────────┘
                        │
                        │ imports from
                        ↓
┌──────────────────────────────────────────────────┐
│  Business Modules (Product Layer)                    │
│  - fnol_triage                                        │
│  - fraud_detection                                    │
│  - ifrs_accrual                                       │
│  - underwriting_scoring                               │
│  - reinsurance_pricing                                │
└──────────────────────────────────────────────────┘
                        │
                        │ imports from
                        ↓
┌──────────────────────────────────────────────────┐
│  Core Platform (Foundation Layer)                    │
│  - decision_engine                                    │
│  - policy_engine                                      │
│  - audit_logging                                      │
│  - telemetry                                          │
│  - security                                           │
│  - governance                                         │
└──────────────────────────────────────────────────┘
                        │
                        │ imports from
                        ↓
┌──────────────────────────────────────────────────┐
│  Standard Library + Pydantic + Logging               │
└──────────────────────────────────────────────────┘
```

**Key Principle**: Dependencies flow **downward only**. Lower layers NEVER import from upper layers.

## Core Module Responsibilities

### decision_engine
**Responsibility**: Orchestrate decision workflows and manage decision lifecycle.

**Owns**:
- Decision types (ADVISORY, BOUNDED, SIMULATION)
- Decision context (user, trace_id, timestamp)
- Decision results (recommendation, confidence, reasoning)
- Decision orchestration logic
- Approval determination

**Does NOT Own**:
- Business logic (belongs in modules/)
- Model inference (belongs in modules/)
- UI rendering (belongs in spaces/)
- Data storage (uses audit_logging)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, Optional
from datetime import datetime
import logging
import uuid

# Pydantic for data models
from pydantic import BaseModel, Field

# Other core services (optional dependencies)
from core.policy_engine import PolicyEnforcer  # Optional
from core.audit_logging import AuditLogger     # Optional
from core.telemetry import TelemetryCollector  # Optional
```

**Forbidden Imports**:
```python
from modules.fnol_triage import *        # ❌ NEVER
from spaces.fnol_space import *          # ❌ NEVER
from transformers import *               # ❌ NEVER
import gradio                            # ❌ NEVER
import torch                             # ❌ NEVER
```

---

### policy_engine
**Responsibility**: Enforce business rules, constraints, and regulatory requirements.

**Owns**:
- Policy definitions
- Policy types (REGULATORY, BUSINESS, OPERATIONAL)
- Constraint validation
- Rule evaluation logic
- Violation reporting

**Does NOT Own**:
- Specific business policies (configured externally)
- Decision execution (belongs in decision_engine)
- Audit storage (belongs in audit_logging)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

# Pydantic
from pydantic import BaseModel, Field

# NO imports from other core modules
# Policy engine is a leaf service
```

**Forbidden Imports**:
```python
from core.decision_engine import *       # ❌ NEVER (creates circular dependency)
from modules.* import *                  # ❌ NEVER
```

---

### audit_logging
**Responsibility**: Provide complete audit trail for all decision-making processes.

**Owns**:
- Audit entry models
- Audit levels (INFO, WARNING, ERROR, CRITICAL)
- Storage backends (in-memory, file, database)
- Immutable audit records
- Query interfaces

**Does NOT Own**:
- Decision logic (belongs in decision_engine)
- Policy enforcement (belongs in policy_engine)
- Long-term analytics (use telemetry)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import logging
import json

# Pydantic
from pydantic import BaseModel, Field

# NO imports from other core modules
```

**Forbidden Imports**:
```python
from core.decision_engine import *       # ❌ NEVER
from core.policy_engine import *         # ❌ NEVER
```

---

### telemetry
**Responsibility**: Provide metrics collection, performance monitoring, and observability.

**Owns**:
- Metric types (Counter, Gauge, Histogram, Timer)
- Metric collection
- Metric aggregation
- Export interfaces (Prometheus, DataDog, etc.)

**Does NOT Own**:
- Audit records (belongs in audit_logging)
- Decision logic (belongs in decision_engine)
- Alerting (external system)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import time
import logging

# Pydantic
from pydantic import BaseModel, Field

# NO imports from other core modules
```

**Forbidden Imports**:
```python
from core.decision_engine import *       # ❌ NEVER
from core.audit_logging import *         # ❌ NEVER
```

---

### security
**Responsibility**: Provide authentication, authorization, and access control.

**Owns**:
- User authentication
- Token management
- Role-based access control (RBAC)
- Permission definitions
- Access control lists (ACLs)

**Does NOT Own**:
- User data storage (external system)
- Decision logic (belongs in decision_engine)
- Audit logging (belongs in audit_logging)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

# Pydantic
from pydantic import BaseModel, Field

# NO imports from other core modules
```

**Forbidden Imports**:
```python
from core.decision_engine import *       # ❌ NEVER
from core.policy_engine import *         # ❌ NEVER
```

---

### governance
**Responsibility**: Provide human-in-the-loop controls, validation, and compliance enforcement.

**Owns**:
- Input validation
- Human oversight workflows
- Approval level determination
- Compliance rule checking
- Justification validation

**Does NOT Own**:
- Decision execution (belongs in decision_engine)
- Policy storage (belongs in policy_engine)
- Audit records (belongs in audit_logging)

**Allowed Imports**:
```python
# Standard library
from typing import Any, Dict, List, Optional
from enum import Enum
import logging

# Pydantic
from pydantic import BaseModel, Field

# Can import from policy_engine (governance uses policies)
from core.policy_engine import Policy, PolicyType

# NO imports from decision_engine (to avoid circular dependency)
```

**Forbidden Imports**:
```python
from core.decision_engine import *       # ❌ NEVER (circular dependency)
from modules.* import *                  # ❌ NEVER
```

---

## Import Dependency Graph

```
decision_engine
    │
    ├─── depends on → policy_engine (optional)
    ├─── depends on → audit_logging (optional)
    └─── depends on → telemetry (optional)

policy_engine
    └─── NO dependencies on other core modules

audit_logging
    └─── NO dependencies on other core modules

telemetry
    └─── NO dependencies on other core modules

security
    └─── NO dependencies on other core modules

governance
    └─── depends on → policy_engine (optional)
```

**Critical Rule**: `decision_engine` is the ONLY core module that can import from other core modules. All other core modules are **leaf services** with no internal dependencies.

## Cross-Module Communication

### Dependency Injection Pattern

Core modules use **dependency injection** to avoid tight coupling:

```python
# ✅ CORRECT: Optional dependencies via constructor
class DecisionOrchestrator:
    def __init__(
        self,
        policy_engine: Optional[Any] = None,  # Optional dependency
        audit_logger: Optional[Any] = None,
        telemetry: Optional[Any] = None
    ):
        self.policy_engine = policy_engine
        self.audit_logger = audit_logger
        self.telemetry = telemetry
    
    def execute_decision(self, ...):
        # Check if service is available before using
        if self.policy_engine:
            validation = self.policy_engine.validate_decision(decision)
```

```python
# ❌ WRONG: Direct instantiation creates tight coupling
class DecisionOrchestrator:
    def __init__(self):
        self.policy_engine = PolicyEnforcer()  # ❌ Hard dependency
```

### Interface Contracts

Core modules define **interface contracts** via type hints:

```python
# policy_engine/models.py
class ValidationResult(BaseModel):
    is_valid: bool
    violations: List[str]
    warnings: List[str]
    policies_checked: List[str]

# decision_engine can depend on this contract
# without importing the implementation
```

## Module Isolation Rules

### 1. No Shared State

Core modules MUST NOT share global state:

```python
# ❌ WRONG: Global state
_global_policies = []  # Shared across modules

def add_policy(policy):
    _global_policies.append(policy)
```

```python
# ✅ CORRECT: Instance state
class PolicyEnforcer:
    def __init__(self):
        self.policies = []  # Instance-specific
    
    def add_policy(self, policy):
        self.policies.append(policy)
```

### 2. No Side Effects in Imports

Importing a core module MUST NOT cause side effects:

```python
# ❌ WRONG: Side effects on import
# __init__.py
logger = logging.getLogger(__name__)
logger.info("Module loaded")  # ❌ Side effect

# Initialize database connection
db = connect_to_database()  # ❌ Side effect
```

```python
# ✅ CORRECT: No side effects
# __init__.py
from .orchestrator import DecisionOrchestrator
from .models import DecisionType, DecisionContext

__all__ = ["DecisionOrchestrator", "DecisionType", "DecisionContext"]
```

### 3. Explicit Public APIs

Each core module MUST define its public API via `__all__`:

```python
# core/decision_engine/__init__.py
__all__ = [
    "DecisionOrchestrator",
    "DecisionType",
    "DecisionContext",
    "DecisionResult",
    "Decision",
]

# Private implementation details are NOT exported
# _internal_helper() is not in __all__
```

### 4. Version Compatibility

Core modules MUST maintain backward compatibility:

```python
# When adding new features, use optional parameters
class DecisionOrchestrator:
    def execute_decision(
        self,
        decision_type: DecisionType,
        input_data: Dict[str, Any],
        context: DecisionContext,
        module_name: str = "unknown",  # Optional, has default
        # New parameter in v1.1.0
        timeout_seconds: Optional[int] = None  # Optional, backward compatible
    ) -> DecisionResult:
        pass
```

## Testing Boundaries

### Unit Test Isolation

Each core module MUST be testable in isolation:

```python
# tests/core/test_policy_engine.py
import pytest
from core.policy_engine import PolicyEnforcer, Policy, PolicyType

def test_policy_validation():
    # No dependencies on other core modules
    enforcer = PolicyEnforcer()
    policy = Policy(
        policy_id="test",
        name="Test Policy",
        description="Test",
        policy_type=PolicyType.BUSINESS,
        rules={"min_confidence": 0.85}
    )
    enforcer.add_policy(policy)
    
    # Test in isolation
    result = enforcer.validate_decision(mock_decision)
    assert result.is_valid
```

### Integration Test Boundaries

Integration tests verify module interactions:

```python
# tests/integration/test_decision_flow.py
from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer, Policy, PolicyType
from core.audit_logging import AuditLogger

def test_full_decision_flow():
    # Test interaction between core modules
    policy_engine = PolicyEnforcer()
    audit_logger = AuditLogger()
    
    orchestrator = DecisionOrchestrator(
        policy_engine=policy_engine,
        audit_logger=audit_logger
    )
    
    # Execute decision
    result = orchestrator.execute_decision(...)
    
    # Verify interactions
    assert result is not None
```

## Enforcement Mechanisms

### 1. Import Linting

Use `pylint` or `flake8` with custom rules:

```ini
# .pylintrc
[MASTER]
forbidden-imports=
    core.decision_engine:modules.*,spaces.*,transformers,gradio,torch
    core.policy_engine:modules.*,spaces.*,core.decision_engine
    core.audit_logging:modules.*,spaces.*,core.decision_engine,core.policy_engine
```

### 2. Pre-commit Hooks

```bash
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: check-core-imports
      name: Check core module import boundaries
      entry: python tools/check_imports.py
      language: python
      files: ^core/
```

### 3. CI/CD Validation

```yaml
# .github/workflows/validate-boundaries.yml
name: Validate Module Boundaries
on: [push, pull_request]
jobs:
  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check import boundaries
        run: python tools/check_imports.py --strict
```

## Migration Checklist

When adding new code to core modules:

- [ ] Does this belong in core, or should it be in modules/?
- [ ] Does this module import from upper layers? (If yes, STOP)
- [ ] Does this module have Hugging Face dependencies? (If yes, STOP)
- [ ] Does this module have UI dependencies? (If yes, STOP)
- [ ] Is the public API defined in `__all__`?
- [ ] Are all dependencies injected via constructor?
- [ ] Are there unit tests that run in isolation?
- [ ] Is the module documented in core/README.md?
- [ ] Are import rules documented in this file?

## Violation Examples

### ❌ Example 1: Core importing from modules

```python
# core/decision_engine/orchestrator.py
from modules.fnol_triage import FNOLEngine  # ❌ WRONG

class DecisionOrchestrator:
    def execute_decision(self, ...):
        engine = FNOLEngine()  # ❌ Business logic in core
```

**Fix**: Business logic belongs in modules/, not core/.

### ❌ Example 2: Circular dependency

```python
# core/policy_engine/enforcer.py
from core.decision_engine import Decision  # ❌ WRONG

class PolicyEnforcer:
    def validate_decision(self, decision: Decision):  # ❌ Circular
        pass
```

**Fix**: Use `Any` type hint or define shared types in a separate module.

```python
# ✅ CORRECT
from typing import Any

class PolicyEnforcer:
    def validate_decision(self, decision: Any):  # ✅ No circular dependency
        pass
```

### ❌ Example 3: Hugging Face in core

```python
# core/decision_engine/orchestrator.py
from transformers import AutoModel  # ❌ WRONG

class DecisionOrchestrator:
    def __init__(self):
        self.model = AutoModel.from_pretrained(...)  # ❌ Model in core
```

**Fix**: Models belong in modules/, not core/.

## Summary

**Golden Rules**:

1. ✅ Core modules are **platform services**, not business logic
2. ✅ Dependencies flow **downward only**
3. ✅ Core modules are **domain-agnostic**
4. ✅ Core modules have **NO Hugging Face dependencies**
5. ✅ Core modules have **NO UI dependencies**
6. ✅ Core modules use **dependency injection**
7. ✅ Core modules define **explicit public APIs**
8. ✅ Core modules are **testable in isolation**

**When in doubt**: If it's specific to FNOL, fraud, IFRS, underwriting, or reinsurance → it belongs in `modules/`, NOT `core/`.
