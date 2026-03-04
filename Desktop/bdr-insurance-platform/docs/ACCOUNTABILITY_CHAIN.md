# Accountability Chain - Phase 2.1

## Overview

The **Accountability Chain** defines the complete ownership hierarchy for every insurance decision. It answers three critical questions:

1. **Who makes the decision?** (Primary Owner)
2. **Who do we escalate to?** (Escalation Owner)
3. **Who is ultimately responsible?** (Ultimate Accountable)

This is not documentation—it's **executable governance** enforced at runtime.

---

## Structure

```python
@dataclass(frozen=True)
class AccountabilityChain:
    primary_owner: DecisionOwner           # Who makes the decision
    escalation_owner: DecisionOwner        # Who to escalate to
    ultimate_accountable: DecisionOwner    # Ultimate responsibility
    override_authority: Literal["human_only", "system_allowed", "committee_required"]
    liability_scope: Literal["advisory", "financial_decision_support", "automated_action"]
    created_at: datetime
```

---

## Components

### 1. Primary Owner

**Who makes the decision?**

- Can be `human`, `system`, or `committee`
- Must be a specific, identifiable entity
- Responsible for the decision outcome

**Examples**:
```python
# Human primary owner
primary = DecisionOwner(
    owner_id="emp_12345",
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="claims_manager",
)

# System primary owner
primary = DecisionOwner(
    owner_id="fnol_triage_v1",
    owner_type="system",
    organization="gig_takaful_kuwait",
    role="automated_decision_system",
)

# Committee primary owner
primary = DecisionOwner(
    owner_id="committee_underwriting",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="underwriting_committee",
)
```

### 2. Escalation Owner

**Who do we escalate to if issues arise?**

- Must be different from primary owner (no self-escalation)
- Typically a supervisor or senior role
- Handles exceptions and edge cases

**Examples**:
```python
# Escalate to supervisor
escalation = DecisionOwner(
    owner_id="emp_67890",
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="senior_claims_manager",
)

# Escalate to committee
escalation = DecisionOwner(
    owner_id="committee_claims",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="claims_committee",
)
```

### 3. Ultimate Accountable

**Who is ultimately responsible (legal/regulatory)?**

- ✅ MUST be `human` or `committee`
- ❌ CANNOT be `system`
- Final authority for legal and regulatory purposes
- Typically a committee or C-level executive

**Examples**:
```python
# Committee ultimate accountable
ultimate = DecisionOwner(
    owner_id="committee_claims",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="claims_committee",
)

# Executive ultimate accountable
ultimate = DecisionOwner(
    owner_id="ceo_gig_takaful",
    owner_type="human",
    organization="gig_takaful_kuwait",
    role="chief_executive_officer",
)
```

### 4. Override Authority

Defines who can override this decision:

- `"human_only"`: Only humans can override (most restrictive)
- `"system_allowed"`: Systems can override within boundaries
- `"committee_required"`: Requires committee approval (highest authority)

**Usage**:
```python
# High-risk decisions require human override
override_authority="human_only"

# Low-risk decisions allow system override
override_authority="system_allowed"

# Critical decisions require committee
override_authority="committee_required"
```

### 5. Liability Scope

Defines the scope of liability:

- `"advisory"`: Provides recommendations only (no direct action)
- `"financial_decision_support"`: Supports financial decisions (bounded)
- `"automated_action"`: Can trigger automated actions (highest risk)

**Rules**:
- ❌ `automated_action` + `system_allowed` override = **FORBIDDEN**
- ✅ `automated_action` requires `human_only` or `committee_required` override

---

## Validation Rules

### Rule 1: No Self-Escalation

```python
# ❌ INVALID - primary and escalation are the same
chain = AccountabilityChain(
    primary_owner=owner_a,
    escalation_owner=owner_a,  # Same as primary!
    ultimate_accountable=owner_b,
    ...
)
# Raises: ValueError("primary_owner and escalation_owner cannot be the same")
```

### Rule 2: Ultimate Accountable Must Be Human/Committee

```python
# ❌ INVALID - system cannot be ultimate accountable
system_owner = DecisionOwner(
    owner_id="ai_system",
    owner_type="system",
    ...
)

chain = AccountabilityChain(
    primary_owner=owner_a,
    escalation_owner=owner_b,
    ultimate_accountable=system_owner,  # System not allowed!
    ...
)
# Raises: ValueError("ultimate_accountable must be a human or committee")
```

### Rule 3: Automated Action Requires Human Override

```python
# ❌ INVALID - automated_action with system_allowed override
chain = AccountabilityChain(
    primary_owner=system_owner,
    escalation_owner=human_owner,
    ultimate_accountable=committee_owner,
    override_authority="system_allowed",  # Not allowed!
    liability_scope="automated_action",
    ...
)
# Raises: ValueError("automated_action liability requires human_only or committee_required override")
```

### Rule 4: Ownership Must Be Fresh

Ownership chains older than **1 year** are considered stale:

```python
from core.governance import validate_ownership_chain

# Raises if ownership is > 1 year old
validate_ownership_chain(ownership)
# Raises: OwnershipViolation("Ownership chain is stale (400 days old)")
```

---

## Common Patterns

### Pattern 1: System-Initiated Decision

**Use Case**: Automated FNOL triage

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

# Result:
# - Primary: fnol_triage_v1 (system)
# - Escalation: emp_12345 (human supervisor)
# - Ultimate: committee_claims (committee)
# - Override: human_only
# - Liability: financial_decision_support
```

### Pattern 2: Human-Initiated Decision

**Use Case**: Claims manager approves a claim

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

# Result:
# - Primary: emp_12345 (human)
# - Escalation: emp_67890 (supervisor)
# - Ultimate: committee_claims (committee)
# - Override: human_only
# - Liability: advisory
```

### Pattern 3: Committee Decision

**Use Case**: High-value claim requires committee approval

```python
primary = DecisionOwner(
    owner_id="committee_claims",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="claims_committee",
)

escalation = DecisionOwner(
    owner_id="committee_executive",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="executive_committee",
)

ultimate = DecisionOwner(
    owner_id="board_directors",
    owner_type="committee",
    organization="gig_takaful_kuwait",
    role="board_of_directors",
)

chain = AccountabilityChain(
    primary_owner=primary,
    escalation_owner=escalation,
    ultimate_accountable=ultimate,
    override_authority="committee_required",
    liability_scope="automated_action",
)
```

---

## Escalation Scenarios

### Scenario 1: Boundary Violation

```
Decision: Auto-approve claim for $75,000
Scope: BOUNDED_MEDIUM (max $50,000)

Action:
1. Boundary check FAILS
2. Decision escalates to escalation_owner
3. Human review required
4. Escalation owner can:
   - Approve with justification
   - Reject
   - Escalate to ultimate_accountable
```

### Scenario 2: Forbidden Action Attempted

```
Decision: System attempts to disburse funds
Scope: BOUNDED_LOW (disburse_funds is forbidden)

Action:
1. Runtime enforcement BLOCKS decision
2. Raises AccountabilityViolation
3. Decision cannot proceed
4. Must be handled by human with appropriate authority
```

### Scenario 3: High-Risk Decision

```
Decision: Fraud investigation recommendation
Scope: ADVISORY (always requires human review)

Action:
1. System provides recommendation
2. Automatically escalates to primary_owner (human)
3. Human reviews and decides
4. If uncertain, escalates to escalation_owner
5. Ultimate_accountable signs off on final decision
```

---

## Audit Trail

### Ownership in Audit Records

Every decision audit record includes ownership metadata:

```json
{
  "decision_id": "dec_123e4567",
  "timestamp": "2026-01-20T18:30:00Z",
  "module": "fnol_triage",
  "decision_type": "bounded",
  "ownership": {
    "decision_owner": "fnol_triage_v1",
    "decision_owner_role": "automated_decision_system",
    "decision_owner_type": "system",
    "escalation_owner": "emp_12345",
    "escalation_owner_role": "claims_manager",
    "ultimate_accountable": "committee_claims",
    "ultimate_accountable_org": "gig_takaful_kuwait",
    "override_authority": "human_only",
    "liability_scope": "financial_decision_support",
    "ownership_created_at": "2026-01-15T10:00:00Z"
  }
}
```

### Audit Queries

**Find all decisions by a specific owner**:
```sql
SELECT * FROM audit_log
WHERE ownership->>'decision_owner' = 'fnol_triage_v1'
```

**Find all decisions requiring committee approval**:
```sql
SELECT * FROM audit_log
WHERE ownership->>'override_authority' = 'committee_required'
```

**Find all automated actions**:
```sql
SELECT * FROM audit_log
WHERE ownership->>'liability_scope' = 'automated_action'
```

---

## Legal & Regulatory Compliance

### Regulatory Requirements

1. **Attributability**: Every decision must be attributable to a specific owner
2. **Accountability**: Clear chain of responsibility for legal review
3. **Auditability**: Complete audit trail with ownership metadata
4. **Enforceability**: Runtime enforcement prevents unauthorized decisions

### Court Admissibility

Accountability chains are designed for court admissibility:

- ✅ Immutable (frozen dataclasses)
- ✅ Timestamped (created_at)
- ✅ Machine-verifiable (runtime enforcement)
- ✅ Complete audit trail (ownership metadata)
- ✅ No anonymous owners (explicit validation)

### Regulatory Audit

Regulators can:

1. Query all decisions by owner
2. Trace escalation chains
3. Verify ultimate accountability
4. Audit override authority usage
5. Review liability scope assignments

---

## Integration Example

### Complete Decision Flow with Ownership

```python
from core.decision_engine import DecisionRequest, DecisionTypeEnum
from core.governance import (
    create_system_ownership,
    get_scope_for_decision_type,
)

# Step 1: Create ownership
ownership = create_system_ownership(
    system_id="fnol_triage_v1",
    organization="gig_takaful_kuwait",
    human_supervisor_id="emp_12345",
    human_supervisor_role="claims_manager",
    ultimate_accountable_id="committee_claims",
    ultimate_accountable_role="claims_committee",
)

# Step 2: Get appropriate scope
scope = get_scope_for_decision_type(
    DecisionTypeEnum.BOUNDED,
    financial_exposure=25000.0,
)

# Step 3: Create decision request
request = DecisionRequest(
    decision_type=DecisionTypeEnum.BOUNDED,
    module_name="fnol_triage",
    input_data={
        "claim_amount": 25000.0,
        "policy_number": "POL-12345",
    },
    user_id="user_123",
    ownership=ownership,
    accountability_scope=scope,
)

# Step 4: Enforce ownership (MANDATORY)
request.enforce_ownership_requirements()

# Step 5: Process decision
response = service.execute(request)

# Step 6: Audit log includes ownership
audit_log = response.to_audit_log()
print(audit_log["ownership"])
```

---

## Best Practices

### 1. Always Use Helper Functions

✅ **Good**:
```python
ownership = create_system_ownership(...)
```

❌ **Bad**:
```python
# Manual construction is error-prone
ownership = AccountabilityChain(
    primary_owner=DecisionOwner(...),
    escalation_owner=DecisionOwner(...),
    ...
)
```

### 2. Match Scope to Financial Exposure

✅ **Good**:
```python
scope = get_scope_for_decision_type(
    DecisionTypeEnum.BOUNDED,
    financial_exposure=claim_amount,
)
```

❌ **Bad**:
```python
# Always using LOW scope regardless of amount
scope = BOUNDED_LOW_SCOPE
```

### 3. Enforce Before Processing

✅ **Good**:
```python
def execute(self, request: DecisionRequest):
    request.enforce_ownership_requirements()  # First!
    # Then process...
```

❌ **Bad**:
```python
def execute(self, request: DecisionRequest):
    # Process first, enforce later (or never)
    result = self.process(request)
    request.enforce_ownership_requirements()  # Too late!
```

### 4. Refresh Stale Ownership

✅ **Good**:
```python
# Check ownership age
age_days = (datetime.utcnow() - ownership.created_at).days
if age_days > 365:
    ownership = create_system_ownership(...)  # Refresh
```

### 5. Document Ownership Decisions

✅ **Good**:
```python
# Document why this ownership structure
ownership = create_system_ownership(
    system_id="fnol_triage_v1",  # Automated triage system
    organization="gig_takaful_kuwait",
    human_supervisor_id="emp_12345",  # Claims manager oversees
    human_supervisor_role="claims_manager",
    ultimate_accountable_id="committee_claims",  # Committee has final say
    ultimate_accountable_role="claims_committee",
)
```

---

## Troubleshooting

### Error: "primary_owner and escalation_owner cannot be the same"

**Cause**: Self-escalation is forbidden.

**Fix**: Use different owners for primary and escalation:
```python
primary = DecisionOwner(owner_id="emp_12345", ...)
escalation = DecisionOwner(owner_id="emp_67890", ...)  # Different!
```

### Error: "ultimate_accountable must be a human or committee"

**Cause**: System cannot be ultimate accountable.

**Fix**: Use human or committee for ultimate accountable:
```python
ultimate = DecisionOwner(
    owner_id="committee_claims",
    owner_type="committee",  # Not "system"!
    ...
)
```

### Error: "automated_action liability requires human_only or committee_required override"

**Cause**: Automated actions cannot have system override.

**Fix**: Use human_only or committee_required:
```python
chain = AccountabilityChain(
    ...
    override_authority="human_only",  # Not "system_allowed"!
    liability_scope="automated_action",
)
```

### Error: "Ownership chain is stale (400 days old)"

**Cause**: Ownership is older than 1 year.

**Fix**: Create fresh ownership:
```python
ownership = create_system_ownership(...)  # Fresh ownership
```

---

## See Also

- [Ownership Model Documentation](./OWNERSHIP_MODEL.md)
- [Decision Contract](../core/decision_engine/contract.py)
- [Governance Module](../core/governance/)
- [Enforcement Rules](../core/governance/enforcement.py)

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: ✅ Production Ready
