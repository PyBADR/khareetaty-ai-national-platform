# Ownership Model - Phase 2.1

## Overview

The Ownership Model provides **immutable, machine-verifiable ownership primitives** for all insurance decisions. Every decision must have explicit ownership, accountability, and enforcement.

**Core Principle**: No anonymous decisions. Every decision is attributable to a specific owner with a clear accountability chain.

---

## Architecture

### 1. DecisionOwner (Immutable Primitive)

```python
@dataclass(frozen=True)
class DecisionOwner:
    owner_id: str              # Unique identifier (e.g., "emp_12345", "fnol_triage_v1")
    owner_type: Literal["human", "system", "committee"]
    organization: str          # Organization unit (e.g., "gig_takaful_kuwait")
    role: str                  # Role (e.g., "claims_manager", "fraud_investigator")
```

**Rules**:
- ✅ `owner_id` must be specific and identifiable
- ❌ No anonymous owners (`"anonymous"`, `"unknown"`, `"system"`, `"auto"`)
- ❌ No empty `owner_id`, `organization`, or `role`
- ✅ Immutable (frozen dataclass)

**Example**:
```python
from core.governance import DecisionOwner

# Valid owner
owner = DecisionOwner(
    owner_id="emp_12345",
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="claims_manager",
)

# Invalid - will raise ValueError
owner = DecisionOwner(
    owner_id="anonymous",  # ❌ Forbidden!
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="claims_manager",
)
```

---

### 2. AccountabilityChain (Complete Ownership Hierarchy)

```python
@dataclass(frozen=True)
class AccountabilityChain:
    primary_owner: DecisionOwner           # Who makes the decision
    escalation_owner: DecisionOwner        # Who to escalate to
    ultimate_accountable: DecisionOwner    # Ultimate responsibility (legal/regulatory)
    override_authority: Literal["human_only", "system_allowed", "committee_required"]
    liability_scope: Literal["advisory", "financial_decision_support", "automated_action"]
    created_at: datetime
```

**Rules**:
- ✅ All three owners must be distinct (no self-escalation)
- ✅ `ultimate_accountable` must be human or committee (not system)
- ✅ `automated_action` liability requires `human_only` or `committee_required` override
- ✅ Immutable (frozen dataclass)

**Example**:
```python
from core.governance import AccountabilityChain, DecisionOwner

primary = DecisionOwner(
    owner_id="fnol_triage_v1",
    owner_type="system",
    organization="gig_takaful_kuwait",
    role="automated_decision_system",
)

escalation = DecisionOwner(
    owner_id="emp_12345",
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="claims_manager",
)

ultimate = DecisionOwner(
    owner_id="committee_claims",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="claims_committee",
)

chain = AccountabilityChain(
    primary_owner=primary,
    escalation_owner=escalation,
    ultimate_accountable=ultimate,
    override_authority="human_only",
    liability_scope="financial_decision_support",
)
```

---

### 3. AccountabilityScope (What Owners Are Responsible For)

```python
@dataclass(frozen=True)
class AccountabilityScope:
    decision_type: DecisionType                    # advisory, bounded, simulation
    allowed_actions: List[str]                     # Actions owner can perform
    forbidden_actions: List[str]                   # Explicitly forbidden actions
    max_impact_level: ImpactLevel                  # 1-5 (MINIMAL to CRITICAL)
    max_financial_exposure: Optional[float]        # Maximum USD exposure
    regulatory_class: RegulatoryClass              # Regulatory sensitivity
    requires_dual_approval: bool                   # Dual approval required?
    audit_retention_days: int                      # Audit retention period
```

**Impact Levels**:
- `MINIMAL (1)`: No financial impact, informational only
- `LOW (2)`: < $1,000 financial impact
- `MEDIUM (3)`: $1,000 - $50,000 financial impact
- `HIGH (4)`: $50,000 - $500,000 financial impact
- `CRITICAL (5)`: > $500,000 or regulatory significance

**Predefined Scopes**:
```python
from core.governance import (
    ADVISORY_SCOPE,
    BOUNDED_LOW_SCOPE,
    BOUNDED_MEDIUM_SCOPE,
    BOUNDED_HIGH_SCOPE,
    SIMULATION_SCOPE,
)
```

**Example**:
```python
from core.governance import BOUNDED_LOW_SCOPE

# Check if action is allowed
if BOUNDED_LOW_SCOPE.is_action_allowed("auto_approve"):
    print("Action allowed")

# Validate financial exposure
is_valid, reason = BOUNDED_LOW_SCOPE.validate_financial_exposure(500.0)
if not is_valid:
    print(f"Violation: {reason}")
```

---

## Runtime Enforcement

### enforce_ownership() - BLOCKING Function

```python
from core.governance import enforce_ownership, OwnershipViolation, AccountabilityViolation

def enforce_ownership(
    decision_request: DecisionRequest,
    ownership: Optional[AccountabilityChain],
    scope: Optional[AccountabilityScope],
) -> None:
    """Enforce ownership requirements. Raises on violations."""
```

**Enforcement Rules**:
1. ✅ Ownership is MANDATORY (raises `OwnershipViolation` if missing)
2. ✅ Accountability scope is MANDATORY (raises `AccountabilityViolation` if missing)
3. ✅ Decision type must match scope
4. ✅ Financial exposure must be within scope limits
5. ✅ Requested actions must be allowed (not forbidden)
6. ✅ Override authority must match owner type

**When to Call**:
- ✅ BEFORE model inference
- ✅ BEFORE DecisionResponse creation
- ✅ Inside DecisionRequest validation

**Example**:
```python
from core.decision_engine import DecisionRequest, DecisionTypeEnum
from core.governance import (
    create_system_ownership,
    BOUNDED_LOW_SCOPE,
    enforce_ownership,
)

# Create ownership
ownership = create_system_ownership(
    system_id="fnol_triage_v1",
    organization="gig_takaful_kuwait",
    human_supervisor_id="emp_12345",
    human_supervisor_role="claims_manager",
    ultimate_accountable_id="committee_claims",
    ultimate_accountable_role="claims_committee",
)

# Create request
request = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name="fnol_triage",
    input_data={"claim_amount": 500.0},
    user_id="user_123",
    ownership=ownership,
    accountability_scope=BOUNDED_LOW_SCOPE,
)

# Enforce ownership (raises on violations)
request.enforce_ownership_requirements()
```

---

## Integration with DecisionRequest

### Updated DecisionRequest

```python
class DecisionRequest(BaseModel):
    decision_id: str
    decision_type: DecisionType
    module_name: str
    input_data: Dict[str, Any]
    user_id: str
    session_id: Optional[str]
    override_boundaries: bool
    metadata: Dict[str, Any]
    
    # Phase 2.1: Ownership & Accountability
    ownership: Optional[AccountabilityChain] = None
    accountability_scope: Optional[AccountabilityScope] = None
    
    def enforce_ownership_requirements(self) -> None:
        """Enforce ownership. Call before processing."""
```

### Production Requirement

In **production** environments:
- ✅ `ownership` is MANDATORY
- ✅ `accountability_scope` is MANDATORY
- ❌ Decisions without ownership will FAIL

In **development/test** environments:
- ⚠️ `ownership` is optional (for gradual migration)
- ⚠️ `accountability_scope` is optional

---

## Audit Integration

### Ownership in Audit Metadata

```python
class AuditMetadata(BaseModel):
    decision_id: str
    timestamp: datetime
    module_name: str
    module_version: str
    user_id: str
    processing_time_ms: int
    environment: str
    audit_trail: Dict[str, Any]
    
    # Phase 2.1: Ownership metadata
    ownership_metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Audit Log Format

```json
{
  "decision_id": "dec_123",
  "timestamp": "2026-01-20T18:30:00Z",
  "module": "fnol_triage",
  "decision_type": "bounded",
  "user_id": "user_789",
  "ownership": {
    "decision_owner": "fnol_triage_v1",
    "decision_owner_role": "automated_decision_system",
    "ultimate_accountable": "committee_claims",
    "ultimate_accountable_org": "gig_takaful_kuwait",
    "override_authority": "human_only",
    "liability_scope": "financial_decision_support"
  }
}
```

---

## Helper Functions

### create_system_ownership()

Create ownership for system-initiated decisions:

```python
from core.governance import create_system_ownership

ownership = create_system_ownership(
    system_id="fnol_triage_v1",
    organization="gig_takaful_kuwait",
    human_supervisor_id="emp_12345",
    human_supervisor_role="claims_manager",
    ultimate_accountable_id="committee_claims",
    ultimate_accountable_role="claims_committee",
)
```

### create_human_ownership()

Create ownership for human-initiated decisions:

```python
from core.governance import create_human_ownership

ownership = create_human_ownership(
    human_id="emp_12345",
    role="claims_manager",
    organization="gig_takaful_kuwait",
    supervisor_id="emp_67890",
    supervisor_role="senior_claims_manager",
    ultimate_accountable_id="committee_claims",
    ultimate_accountable_role="claims_committee",
)
```

### get_scope_for_decision_type()

Get appropriate scope based on decision type and financial exposure:

```python
from core.governance import get_scope_for_decision_type
from core.decision_engine import DecisionTypeEnum

scope = get_scope_for_decision_type(
    DecisionTypeEnum.BOUNDED,
    financial_exposure=25000.0,
)
# Returns BOUNDED_MEDIUM_SCOPE
```

---

## CI/CD Enforcement

### check_ownership.py

CI tool that scans codebase for ownership violations:

```bash
python tools/governance/check_ownership.py
```

**What it checks**:
- ✅ All `DecisionRequest` instantiations have `ownership`
- ✅ All `DecisionRequest` instantiations have `accountability_scope`
- ✅ Scans `core/`, `modules/`, `spaces/` directories
- ❌ Fails CI build if violations found

**Exit codes**:
- `0`: No violations
- `1`: Violations found (CI FAILS)
- `2`: Script error

---

## Migration Guide

### Step 1: Add Ownership to Existing Modules

```python
# Before (Phase 1)
request = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name="fnol_triage",
    input_data={"claim_amount": 500.0},
    user_id="user_123",
)

# After (Phase 2.1)
ownership = create_system_ownership(
    system_id="fnol_triage_v1",
    organization="gig_takaful_kuwait",
    human_supervisor_id="emp_12345",
    human_supervisor_role="claims_manager",
    ultimate_accountable_id="committee_claims",
    ultimate_accountable_role="claims_committee",
)

scope = get_scope_for_decision_type(
    DecisionTypeEnum.BOUNDED,
    financial_exposure=500.0,
)

request = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name="fnol_triage",
    input_data={"claim_amount": 500.0},
    user_id="user_123",
    ownership=ownership,  # ✅ Added
    accountability_scope=scope,  # ✅ Added
)

# Enforce before processing
request.enforce_ownership_requirements()
```

### Step 2: Update Service Contracts

All service contracts must inject ownership:

```python
class FNOLTriageServiceContract:
    def execute(self, request: DecisionRequest) -> DecisionResponse:
        # Enforce ownership FIRST
        request.enforce_ownership_requirements()
        
        # Then proceed with decision logic
        ...
```

### Step 3: Run CI Check

```bash
python tools/governance/check_ownership.py
```

Fix any violations before merging.

---

## Testing

### Run Governance Tests

```bash
pytest tools/governance/test_governance.py -v
```

**Test coverage**:
- ✅ DecisionOwner validation
- ✅ AccountabilityChain validation
- ✅ AccountabilityScope enforcement
- ✅ Runtime enforcement
- ✅ Helper functions
- ✅ DecisionRequest integration

---

## Legal & Regulatory Compliance

### Why This Matters

1. **Regulatory Audit**: Every decision is attributable to a specific owner
2. **Legal Liability**: Clear accountability chain for legal review
3. **Court Admissibility**: Machine-verifiable ownership records
4. **Insurance Compliance**: Meets regulatory requirements for decision transparency

### Audit Retention

- **Standard**: 7 years (2555 days)
- **Highly Regulated**: 7 years minimum
- **Simulation**: 1 year minimum

### Ownership Refresh

Ownership chains older than **1 year** are considered stale and must be refreshed.

---

## FAQ

### Q: Can I skip ownership in development?
A: Yes, but only in `development` or `test` environments. Production REQUIRES ownership.

### Q: What if I don't know the ultimate accountable?
A: You MUST identify the ultimate accountable entity. This is non-negotiable for regulatory compliance.

### Q: Can a system be the ultimate accountable?
A: No. Ultimate accountability must rest with a human or committee.

### Q: What happens if I violate ownership rules?
A: The decision will FAIL with `OwnershipViolation` or `AccountabilityViolation`. No warnings, no bypasses.

### Q: How do I handle legacy code?
A: Gradually migrate by adding ownership to new decisions first, then backfill legacy code. Use the CI tool to track progress.

---

## See Also

- [Accountability Chain Documentation](./ACCOUNTABILITY_CHAIN.md)
- [Decision Contract](../core/decision_engine/contract.py)
- [Governance Module](../core/governance/)
- [CI Enforcement Tool](../tools/governance/check_ownership.py)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: ✅ Production Ready
