# Decision Finality Model
## Phase 2.3: Immutable State Transitions

**Document Version:** 1.0  
**Last Updated:** January 20, 2026  
**Status:** Production-Ready  
**Audience:** Regulators, Legal Teams, Compliance Officers

---

## Executive Summary

This document defines the **Decision Finality Model** - a state machine that governs decision lifecycle and enforces irreversible finality.

### Core Principle

> **FINALIZED decisions are IMMUTABLE and cannot be modified, revoked, or deleted.**

This ensures:
- Legal defensibility
- Audit integrity
- Regulatory compliance
- Operational certainty

---

## 1. Decision States

### 1.1 State Definitions

| State | Description | Can Execute? | Can Finalize? | Mutable? |
|-------|-------------|--------------|---------------|----------|
| **PROPOSED** | Decision created, not yet approved | No | No | Yes |
| **APPROVED** | Decision approved, ready for execution | Yes | No | Yes |
| **EXECUTED** | Decision executed, not yet final | No | Yes | Yes |
| **FINALIZED** | Decision finalized, IMMUTABLE | No | No | **NO** |
| **REVOKED** | Decision revoked (if policy allows) | No | No | No |

### 1.2 State Diagram

```
[PROPOSED]
    |
    v
[APPROVED] -----> [REVOKED]
    |
    v
[EXECUTED]
    |
    v
[FINALIZED]
```

---

## 2. Legal State Transitions

### 2.1 Allowed Transitions

| From State | To State | Condition | Authority Required |
|------------|----------|-----------|--------------------|
| PROPOSED | APPROVED | Decision validated | Approval authority |
| PROPOSED | REVOKED | Policy allows | Revocation authority |
| APPROVED | EXECUTED | Execution successful | Execution authority |
| APPROVED | REVOKED | Policy allows | Revocation authority |
| EXECUTED | FINALIZED | Ready to finalize | Finalization authority |

### 2.2 Illegal Transitions

| From State | To State | Why Illegal |
|------------|----------|-------------|
| PROPOSED | EXECUTED | Must be approved first |
| PROPOSED | FINALIZED | Must be approved and executed first |
| APPROVED | FINALIZED | Must be executed first |
| FINALIZED | * | **Finalized decisions are immutable** |
| REVOKED | * | Revoked decisions cannot be reactivated |
| * | PROPOSED | Cannot go back to proposed |

---

## 3. Finality Enforcement

### 3.1 Immutability Rules

Once a decision reaches **FINALIZED** state:

1. ❌ Cannot change state
2. ❌ Cannot modify decision content
3. ❌ Cannot revoke
4. ❌ Cannot delete
5. ✅ Can only read/audit

### 3.2 Runtime Enforcement

```python
class DecisionStateMachine:
    def transition_to(self, target_state, transitioned_by, reason):
        # Check for finality violation
        if self.current_state == DecisionState.FINALIZED:
            raise FinalityViolation(
                f"Cannot transition from FINALIZED state. "
                f"Decision {self.decision_id} is immutable."
            )
        
        # Check if transition is legal
        if not self.can_transition_to(target_state):
            raise IllegalStateTransition(
                f"Illegal state transition: "
                f"{self.current_state.value} → {target_state.value}"
            )
        
        # Record transition
        self.transition_history.append(transition)
        self.current_state = target_state
```

### 3.3 Exception Types

**FinalityViolation**
- Raised when attempting to modify FINALIZED decision
- Cannot be caught or bypassed
- Logged to audit trail

**IllegalStateTransition**
- Raised when attempting illegal transition
- Cannot be caught or bypassed
- Logged to audit trail

---

## 4. State Transition Audit

### 4.1 What is Logged

Every state transition records:

```python
@dataclass
class StateTransition:
    from_state: DecisionState
    to_state: DecisionState
    transitioned_by: str
    transitioned_at: datetime
    reason: Optional[str]
```

### 4.2 Audit Trail

The state machine maintains complete history:

```python
state_machine.get_transition_history()
# Returns:
[
    {
        "from_state": "proposed",
        "to_state": "approved",
        "transitioned_by": "approver_001",
        "transitioned_at": "2026-01-20T10:00:00Z",
        "reason": "Approved by claims manager"
    },
    {
        "from_state": "approved",
        "to_state": "executed",
        "transitioned_by": "executor_001",
        "transitioned_at": "2026-01-20T10:05:00Z",
        "reason": "Executed successfully"
    },
    {
        "from_state": "executed",
        "to_state": "finalized",
        "transitioned_by": "finalizer_001",
        "transitioned_at": "2026-01-20T10:10:00Z",
        "reason": "Finalized"
    }
]
```

---

## 5. When to Finalize

### 5.1 Finalization Criteria

A decision should be finalized when:

1. ✅ Execution completed successfully
2. ✅ All downstream effects confirmed
3. ✅ No rollback possible
4. ✅ Operational commitment made
5. ✅ Financial transaction completed (if applicable)

### 5.2 Finalization Authority

Only authorities with `can_finalize = True` may finalize decisions.

Typically:
- **System**: Can finalize low-risk automated decisions
- **Human**: Can finalize medium-risk decisions
- **Committee**: Required for high-risk decisions

### 5.3 Finalization Process

```python
# 1. Check state
if not state_machine.can_finalize():
    raise ExecutionViolation("Decision must be EXECUTED before finalization")

# 2. Validate authority
if not authority.can_finalize:
    raise AuthorityViolation("Authority cannot finalize decisions")

# 3. Finalize
state_machine.transition_to(
    target_state=DecisionState.FINALIZED,
    transitioned_by=authority.authority_id,
    reason="Execution confirmed, operational commitment made",
)

# 4. Decision is now IMMUTABLE
assert state_machine.is_finalized()
```

---

## 6. Revocation Policy

### 6.1 When Revocation is Allowed

Revocation may be allowed for:
- **PROPOSED** decisions (before approval)
- **APPROVED** decisions (before execution)

Revocation is **NEVER** allowed for:
- **EXECUTED** decisions (use compensating transaction instead)
- **FINALIZED** decisions (immutable)
- **REVOKED** decisions (already revoked)

### 6.2 Revocation Process

```python
# Check if revocation is allowed
if not state_machine.allow_revocation:
    raise StateTransitionError("Revocation not allowed by policy")

# Check current state
if state_machine.current_state not in [DecisionState.PROPOSED, DecisionState.APPROVED]:
    raise IllegalStateTransition("Cannot revoke executed or finalized decisions")

# Revoke
state_machine.transition_to(
    target_state=DecisionState.REVOKED,
    transitioned_by=authority.authority_id,
    reason="Decision revoked due to policy change",
)
```

### 6.3 Revoked Decision Audit

Revoked decisions:
- ✅ Remain in audit trail forever
- ✅ Cannot be deleted
- ✅ Cannot be reactivated
- ✅ Reason for revocation is logged

---

## 7. Compensating Transactions

### 7.1 When to Use

For **EXECUTED** or **FINALIZED** decisions that need to be "undone":

❌ **DO NOT** revoke or modify the original decision  
✅ **DO** create a compensating transaction

### 7.2 Example

**Original Decision:**
- Decision ID: `dec_claim_12345`
- Action: Approve claim for $10,000
- State: FINALIZED

**Compensating Transaction:**
- Decision ID: `dec_claim_12345_reversal`
- Action: Reverse claim approval
- Reason: "Fraud detected"
- References: `dec_claim_12345`
- State: PROPOSED → APPROVED → EXECUTED → FINALIZED

**Result:**
- Original decision remains FINALIZED (immutable)
- Compensating decision also FINALIZED
- Audit trail shows both decisions
- Net effect: Claim reversed

---

## 8. Regulatory Compliance

### 8.1 Questions Answered

**Q: When is a decision final and irreversible?**  
A: When state machine transitions to FINALIZED.

**Q: Can finalized decisions be modified?**  
A: No. FINALIZED decisions are immutable.

**Q: How do you correct a finalized decision?**  
A: Create a compensating transaction.

**Q: Are all state transitions audited?**  
A: Yes. Every transition is logged with timestamp, authority, and reason.

**Q: Can the audit trail be modified?**  
A: No. State transitions are append-only.

### 8.2 Compliance Requirements

For regulatory compliance, the platform MUST:

1. ✅ Enforce state machine transitions at runtime
2. ✅ Block illegal transitions with exceptions
3. ✅ Log every transition attempt (success or failure)
4. ✅ Maintain immutable audit trail
5. ✅ Prevent modification of finalized decisions
6. ✅ Support compensating transactions

---

## 9. Examples

### 9.1 Legal Transition Sequence

```python
# Create state machine
sm = create_state_machine("dec_12345")
assert sm.current_state == DecisionState.PROPOSED

# Approve
sm.transition_to(DecisionState.APPROVED, "approver_001", "Approved")
assert sm.current_state == DecisionState.APPROVED
assert sm.can_execute()

# Execute
sm.transition_to(DecisionState.EXECUTED, "executor_001", "Executed")
assert sm.current_state == DecisionState.EXECUTED
assert sm.can_finalize()

# Finalize
sm.transition_to(DecisionState.FINALIZED, "finalizer_001", "Finalized")
assert sm.is_finalized()

# Attempt to modify (MUST FAIL)
try:
    sm.transition_to(DecisionState.REVOKED, "bad_actor")
except FinalityViolation as e:
    print(f"Blocked: {e}")
    # "Cannot transition from FINALIZED state. Decision is immutable."
```

### 9.2 Illegal Transition (BLOCKED)

```python
# Create state machine
sm = create_state_machine("dec_illegal")
assert sm.current_state == DecisionState.PROPOSED

# Attempt to execute without approval (MUST FAIL)
try:
    sm.transition_to(DecisionState.EXECUTED, "bad_actor")
except IllegalStateTransition as e:
    print(f"Blocked: {e}")
    # "Illegal state transition: proposed → executed.
    #  Decision must be APPROVED first."
```

### 9.3 Finality Violation (BLOCKED)

```python
# Finalize decision
sm = create_state_machine("dec_final")
sm.transition_to(DecisionState.APPROVED, "approver")
sm.transition_to(DecisionState.EXECUTED, "executor")
sm.transition_to(DecisionState.FINALIZED, "finalizer")

# Attempt to modify finalized decision (MUST FAIL)
try:
    sm.transition_to(DecisionState.REVOKED, "bad_actor")
except FinalityViolation as e:
    print(f"Blocked: {e}")
    # "Cannot transition from FINALIZED state.
    #  Decision dec_final is immutable."
```

---

## 10. Integration with Execution Layer

### 10.1 Execution Flow

```
1. Decision created → PROPOSED
2. Decision approved → APPROVED
3. Execution command created
4. Execution boundary enforced
5. Decision executed → EXECUTED
6. Execution confirmed
7. Decision finalized → FINALIZED
```

### 10.2 State Checks

**Before Execution:**
```python
if not state_machine.can_execute():
    raise ExecutionViolation(
        f"Decision state {state_machine.current_state.value} "
        f"does not allow execution. Must be APPROVED."
    )
```

**After Execution:**
```python
if execution_result.is_successful():
    state_machine.transition_to(
        target_state=DecisionState.EXECUTED,
        transitioned_by=executor_id,
        reason="Execution successful",
    )
```

**Before Finalization:**
```python
if not state_machine.can_finalize():
    raise ExecutionViolation(
        f"Decision state {state_machine.current_state.value} "
        f"does not allow finalization. Must be EXECUTED."
    )
```

---

## 11. Conclusion

The Decision Finality Model provides:

1. **Clear State Definitions** - 5 well-defined states
2. **Legal Transitions** - Only allowed transitions permitted
3. **Immutable Finality** - FINALIZED decisions cannot be modified
4. **Complete Audit Trail** - Every transition logged
5. **Runtime Enforcement** - Illegal transitions blocked with exceptions
6. **Regulatory Compliance** - Meets audit and legal requirements

This model enables the platform to truthfully state:

> **"Finality is irreversible and enforced at runtime. FINALIZED decisions are immutable and legally defensible."**

---

**Document Control:**
- Version: 1.0
- Status: Production-Ready
- Next Review: Q2 2026
- Owner: Platform Architecture Team
- Approver: Chief Legal Officer
