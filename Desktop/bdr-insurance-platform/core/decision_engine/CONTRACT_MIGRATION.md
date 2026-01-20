# Decision Contract Migration Guide

**Version:** 2.0.0 (Contract-First)  
**Status:** MANDATORY for all new modules  
**Migration Deadline:** All modules must migrate by Q2 2026

---

## Overview

The **Decision Contract** is the single source of truth for all insurance decisions in the BDR platform. It enforces:

- ✅ **Single decision shape** across all products
- ✅ **Mandatory human-in-the-loop** enforcement
- ✅ **Complete explainability** (not optional)
- ✅ **Full audit trail** for compliance
- ✅ **Boundary checking** for risk management

**Raw dicts are FORBIDDEN.** All modules MUST return `DecisionResponse`.

---

## Contract Components

### 1. DecisionRequest (Input)

```python
from core.decision_engine import DecisionRequest, DecisionTypeEnum

request = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name="fnol_triage",
    input_data={...},  # Module-specific input
    user_id="user_123",
    session_id="sess_abc",  # Optional
    override_boundaries=False,  # Requires elevated permissions
)
```

**Fields:**
- `decision_id`: Auto-generated UUID
- `decision_type`: ADVISORY | BOUNDED | SIMULATION
- `module_name`: Name of the decision module
- `input_data`: Module-specific input (validated separately)
- `user_id`: User requesting the decision
- `session_id`: Optional session tracking
- `override_boundaries`: Bypass boundary checks (requires permission)
- `metadata`: Additional request metadata

---

### 2. DecisionResponse (Output)

```python
from core.decision_engine import DecisionResponse

response: DecisionResponse = service.execute(request)

# Check if actionable
if response.is_actionable():
    # Can be acted upon automatically
    execute_decision(response.decision_output)
else:
    # Requires human review
    route_to_human(response)
```

**Fields:**
- `decision_id`: Unique identifier
- `decision_type`: Type of decision
- `decision_output`: Module-specific output (dict)
- `boundaries`: BoundaryResult with all checks
- `explainability`: Mandatory explainability payload
- `audit_metadata`: Complete audit trail
- `human_review_required`: Explicit flag
- `human_review_reason`: Why review is needed
- `actionable`: Can be acted upon automatically
- `errors`: Any errors encountered

**Methods:**
- `is_actionable()`: Check if decision can be automated
- `get_review_summary()`: Get human-readable review summary
- `get_confidence_level()`: Get 'high'/'medium'/'low' confidence
- `to_audit_log()`: Convert to audit log format

---

### 3. BoundaryResult (Enforcement)

```python
from core.decision_engine import (
    BoundaryResult,
    BoundaryCheck,
    BoundaryType,
    create_boundary_result,
)

checks = [
    BoundaryCheck(
        boundary_type=BoundaryType.MONETARY,
        name="High Value Threshold",
        threshold=50000.0,
        actual_value=claim_amount,
        passed=claim_amount <= 50000.0,
        reason="Claim amount within threshold",
    ),
    # ... more checks
]

boundaries = create_boundary_result(checks)

if boundaries.requires_human():
    print(boundaries.get_failure_summary())
```

**Boundary Types:**
- `MONETARY`: Dollar amount thresholds
- `CONFIDENCE`: Model confidence thresholds
- `RISK`: Risk score thresholds
- `COMPLEXITY`: Decision complexity
- `REGULATORY`: Regulatory compliance
- `POLICY`: Business policy constraints

---

### 4. Explainability (Mandatory)

```python
from core.decision_engine import (
    Explainability,
    DecisionFactor,
    ScoredSignal,
    Evidence,
)

explainability = Explainability(
    summary="High-value claim requires review",
    key_factors=[
        DecisionFactor(
            name="claim_amount",
            value=75000.0,
            weight=0.8,
            impact="negative",
            description="Claim amount above threshold",
        ),
    ],
    scored_signals=[...],
    evidence=[...],
    confidence_score=0.85,
    model_version="fnol_v2.0.0",
)

# Get top factors
top_3 = explainability.get_top_factors(n=3)

# Get triggered signals
alerts = explainability.get_triggered_signals()
```

**Requirements:**
- Minimum 10-character summary
- At least 1 key factor
- Confidence score (0.0 to 1.0)
- Model version for audit trail

---

### 5. AuditMetadata (Compliance)

```python
from core.decision_engine import AuditMetadata
from datetime import datetime

audit = AuditMetadata(
    decision_id=request.decision_id,
    timestamp=datetime.utcnow(),
    module_name="fnol_triage",
    module_version="2.0.0",
    user_id=request.user_id,
    session_id=request.session_id,
    processing_time_ms=145,
    environment="production",
    audit_trail={...},
)
```

---

## Migration Steps

### Step 1: Update Service Signature

**Before (Legacy):**
```python
def run_fnol_triage(
    input_data: FNOLInput,
    user_id: str,
) -> FNOLOutput:
    # ...
    return FNOLOutput(...)
```

**After (Contract):**
```python
def execute(
    request: DecisionRequest,
) -> DecisionResponse:
    # Parse input
    input_data = self._parse_input(request.input_data)
    
    # Run engine
    result = self.engine.process(input_data)
    
    # Check boundaries
    boundaries = self._check_boundaries(input_data, result)
    
    # Generate explainability
    explainability = self._generate_explainability(input_data, result)
    
    # Build response
    return DecisionResponse(
        decision_id=request.decision_id,
        decision_type=request.decision_type,
        decision_output={...},
        boundaries=boundaries,
        explainability=explainability,
        audit_metadata=audit_metadata,
        human_review_required=self._requires_human_review(...),
        actionable=...,
    )
```

---

### Step 2: Implement Boundary Checks

```python
def _check_boundaries(
    self,
    input_data,
    result,
) -> BoundaryResult:
    checks = []
    
    # Check 1: Monetary threshold
    checks.append(
        BoundaryCheck(
            boundary_type=BoundaryType.MONETARY,
            name="High Value Threshold",
            threshold=50000.0,
            actual_value=float(input_data.amount),
            passed=float(input_data.amount) <= 50000.0,
            reason=f"Amount ${input_data.amount:,.2f}",
        )
    )
    
    # Check 2: Confidence threshold
    checks.append(
        BoundaryCheck(
            boundary_type=BoundaryType.CONFIDENCE,
            name="Minimum Confidence",
            threshold=0.7,
            actual_value=result.confidence,
            passed=result.confidence >= 0.7,
            reason=f"Confidence {result.confidence:.2%}",
        )
    )
    
    return create_boundary_result(checks)
```

---

### Step 3: Generate Explainability

```python
def _generate_explainability(
    self,
    input_data,
    result,
) -> Explainability:
    return Explainability(
        summary=self._generate_summary(result),
        key_factors=[
            DecisionFactor(
                name="amount",
                value=float(input_data.amount),
                weight=0.8,
                impact="negative" if input_data.amount > 50000 else "neutral",
                description=f"Claim amount: ${input_data.amount:,.2f}",
            ),
        ],
        scored_signals=[...],
        evidence=[...],
        confidence_score=result.confidence,
        model_version=self.MODULE_VERSION,
    )
```

---

### Step 4: Determine Human Review

```python
def _requires_human_review(
    self,
    request: DecisionRequest,
    result,
    boundaries: BoundaryResult,
) -> bool:
    # Override if requested
    if request.override_boundaries:
        return False
    
    # Advisory always requires human
    if request.decision_type == DecisionTypeEnum.ADVISORY:
        return True
    
    # Boundary failures require human
    if not boundaries.all_passed:
        return True
    
    # Module-specific rules
    if result.risk_level == "HIGH":
        return True
    
    return False
```

---

## Actionability Rules

A decision is **actionable** (can be automated) if and only if:

1. ✅ Decision type is `BOUNDED`
2. ✅ All boundary checks passed
3. ✅ No human review required
4. ✅ No errors occurred

```python
if response.is_actionable():
    # Safe to automate
    execute_automatically(response)
else:
    # Route to human
    route_to_human_review(response)
```

---

## Module Compliance Checklist

### ✅ FNOL Triage
- [x] Contract-compliant service created (`service_contract.py`)
- [x] Boundary checks implemented (4 checks)
- [x] Explainability generated
- [x] Human review logic defined
- [x] Imports verified

### ⏳ Fraud Detection
- [ ] Contract-compliant service
- [ ] Boundary checks
- [ ] Explainability
- [ ] Human review logic

### ⏳ IFRS Accrual
- [ ] Contract-compliant service
- [ ] Boundary checks
- [ ] Explainability
- [ ] Human review logic

### ⏳ Underwriting Scoring
- [ ] Contract-compliant service
- [ ] Boundary checks
- [ ] Explainability
- [ ] Human review logic

### ⏳ Reinsurance Pricing
- [ ] Contract-compliant service
- [ ] Boundary checks
- [ ] Explainability
- [ ] Human review logic

---

## Architectural Compliance

### ✅ Import Rules (ENFORCED)

```python
# ✅ CORRECT: Core imports from contract
from core.decision_engine import DecisionRequest, DecisionResponse

# ✅ CORRECT: Modules import from core
from core.decision_engine import ...
from core.security import require_permission
from core.audit_logging import AuditLogger

# ❌ FORBIDDEN: Core imports from modules
# from modules.fnol_triage import ...  # NEVER in core/

# ❌ FORBIDDEN: Spaces import from core
# from core.decision_engine import ...  # NEVER in spaces/

# ✅ CORRECT: Spaces import from modules only
from modules.fnol_triage.service_contract import FNOLTriageServiceContract
```

### Dependency Flow

```
spaces/
  ↓ (imports from)
modules/
  ↓ (imports from)
core/
  ↓ (no upward imports)
```

---

## Testing Contract Compliance

```bash
# Test 1: Import contract
python3 -c "from core.decision_engine.contract import DecisionResponse; print('✓')"

# Test 2: Import service
python3 -c "from modules.fnol_triage.service_contract import FNOLTriageServiceContract; print('✓')"

# Test 3: Create request
python3 -c "
from core.decision_engine import DecisionRequest, DecisionTypeEnum
req = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name='fnol_triage',
    input_data={},
    user_id='test_user',
)
print('✓ Request created:', req.decision_id)
"
```

---

## Common Pitfalls

### ❌ Returning Raw Dicts

```python
# FORBIDDEN
def execute(request):
    return {"result": "approved"}  # ❌ Raw dict
```

### ✅ Return DecisionResponse

```python
# CORRECT
def execute(request: DecisionRequest) -> DecisionResponse:
    return DecisionResponse(...)  # ✅ Contract type
```

---

### ❌ Skipping Explainability

```python
# FORBIDDEN
explainability = None  # ❌ Explainability is MANDATORY
```

### ✅ Always Provide Explainability

```python
# CORRECT
explainability = Explainability(
    summary="...",
    key_factors=[...],
    confidence_score=0.85,
    model_version="v2.0.0",
)  # ✅ Complete explainability
```

---

### ❌ Ignoring Boundaries

```python
# FORBIDDEN
boundaries = None  # ❌ Boundaries are MANDATORY
```

### ✅ Always Check Boundaries

```python
# CORRECT
boundaries = self._check_boundaries(input_data, result)
if not boundaries.all_passed:
    human_review_required = True
```

---

## Support

- **Documentation:** `core/decision_engine/README.md`
- **Examples:** `modules/fnol_triage/service_contract.py`
- **Questions:** Contact platform team

---

## Version History

- **2.0.0** (2026-01-20): Contract-First implementation
  - Added DecisionRequest/DecisionResponse
  - Added BoundaryResult enforcement
  - Added mandatory Explainability
  - Added AuditMetadata
  - FNOL module migrated

- **1.0.0** (2026-01-15): Legacy implementation
  - DecisionOrchestrator
  - DecisionType enum
  - DecisionContext/DecisionResult

---

**END OF MIGRATION GUIDE**
