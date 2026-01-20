# Responsibility Contract
## Phase 2.3: Operational Accountability

**Document Version:** 1.0  
**Last Updated:** January 20, 2026  
**Status:** Production-Ready  
**Audience:** Operations Teams, SRE, Platform Engineers

---

## Executive Summary

This document defines the **Responsibility Contract** - a formal specification of operational responsibility for decision execution.

### Core Principle

> **Authority ≠ Responsibility**

- **Authority** = Who can decide (legal/regulatory)
- **Responsibility** = Who operates it (operational)

Both are required for production execution.

---

## 1. Concept

### 1.1 What is a Responsibility Contract?

A **ResponsibilityContract** is an immutable specification that defines:

1. Which system executes the decision
2. Which team operates the system
3. Who is the operational owner
4. What SLA applies
5. Who to escalate to if execution fails

### 1.2 Why Separate from Authority?

| Aspect | Authority | Responsibility |
|--------|-----------|----------------|
| **Domain** | Legal / Regulatory | Operational |
| **Question** | Who can approve? | Who executes? |
| **Example** | Claims Manager | Claims Processing System |
| **Enforced by** | Governance layer | Execution layer |
| **Required for** | Decision approval | Decision execution |
| **Expires** | Yes (time-bound) | No (operational) |

---

## 2. Structure

### 2.1 Data Model

```python
@dataclass(frozen=True)
class ResponsibilityContract:
    contract_id: str
    responsible_system: str
    responsible_team: str
    operational_owner: str
    sla_class: SLAClass
    escalation_contact: str
```

### 2.2 Field Definitions

| Field | Type | Description | Example |
|-------|------|-------------|----------|
| **contract_id** | str | Unique contract identifier | `resp_claims_ops_kw` |
| **responsible_system** | str | System that executes decision | `claims_processing_system` |
| **responsible_team** | str | Team that operates system | `claims_operations_kuwait` |
| **operational_owner** | str | Individual operational owner | `ops_manager_kw` |
| **sla_class** | SLAClass | SLA classification | `HIGH` |
| **escalation_contact** | str | Escalation contact | `escalation@gigkuwait.com` |

### 2.3 Validation Rules

1. ✅ All fields are required (no optional fields)
2. ✅ contract_id must be unique
3. ✅ responsible_system must be a valid system identifier
4. ✅ operational_owner must be a valid user identifier
5. ✅ escalation_contact must be a valid email or contact

---

## 3. SLA Classes

### 3.1 Definitions

| SLA Class | Response Time | Use Case | Example |
|-----------|---------------|----------|----------|
| **CRITICAL** | < 1 minute | Emergency claims, life-threatening | Emergency medical claim |
| **HIGH** | < 5 minutes | High-value claims, urgent | Motor accident claim |
| **MEDIUM** | < 30 minutes | Standard claims | Property damage claim |
| **LOW** | < 4 hours | Low-priority tasks | Document upload |
| **BEST_EFFORT** | No guarantee | Background jobs, analytics | Report generation |

### 3.2 SLA Enforcement

SLA classes are:
- ✅ Documented in responsibility contract
- ✅ Monitored by operations team
- ✅ Reported in execution metrics
- ❌ NOT enforced by code (operational concern)

---

## 4. Creating Responsibility Contracts

### 4.1 Helper Function

```python
def create_responsibility_contract(
    responsible_system: str,
    responsible_team: str,
    operational_owner: str,
    sla_class: SLAClass,
    escalation_contact: str,
) -> ResponsibilityContract:
    """
    Create a responsibility contract.
    
    Args:
        responsible_system: System responsible for execution
        responsible_team: Team responsible for operations
        operational_owner: Individual operational owner
        sla_class: SLA classification
        escalation_contact: Escalation contact
    
    Returns:
        Immutable ResponsibilityContract
    """
    import uuid
    
    return ResponsibilityContract(
        contract_id=f"resp_{uuid.uuid4().hex[:12]}",
        responsible_system=responsible_system,
        responsible_team=responsible_team,
        operational_owner=operational_owner,
        sla_class=sla_class,
        escalation_contact=escalation_contact,
    )
```

### 4.2 Example

```python
contract = create_responsibility_contract(
    responsible_system="claims_processing_system",
    responsible_team="claims_operations_kuwait",
    operational_owner="ops_manager_kw",
    sla_class=SLAClass.HIGH,
    escalation_contact="escalation@gigkuwait.com",
)
```

---

## 5. Enforcement

### 5.1 When is it Required?

**Production Execution:**
- ✅ ResponsibilityContract REQUIRED
- ✅ Validated before execution
- ✅ Logged in audit trail

**Non-Production Execution:**
- ⚠️ ResponsibilityContract OPTIONAL
- ⚠️ Warning logged if missing
- ✅ Execution allowed

### 5.2 Enforcement Logic

```python
def enforce_execution_boundary(
    command: DecisionCommand,
    state_machine: DecisionStateMachine,
    authority: DecisionAuthority,
    authority_anchor: AuthorityAnchor,
    responsibility: ResponsibilityContract,
    requesting_system: str,
) -> None:
    # ... other checks ...
    
    # Check 4: Responsibility contract (production only)
    if command.requires_production_gate():
        if not responsibility:
            raise ExecutionViolation(
                f"Production execution requires ResponsibilityContract. "
                f"Command {command.command_id} has no responsibility contract."
            )
```

---

## 6. Integration with Execution

### 6.1 Execution Flow

```
1. DecisionCommand created
2. ResponsibilityContract attached
3. Execution boundary enforced
   ├─ Authority validated
   ├─ Responsibility validated ← HERE
   └─ State machine checked
4. Decision executed by responsible_system
5. ExecutionResult created
6. Audit trail includes responsibility metadata
```

### 6.2 Executor Integration

```python
class DecisionExecutor:
    def execute(
        self,
        command: DecisionCommand,
        state_machine: DecisionStateMachine,
        responsibility: ResponsibilityContract,
        authority_validated: bool = False,
    ) -> ExecutionResult:
        # Check 3: Responsibility contract must be present
        if not responsibility:
            return create_blocked_result(
                command_id=command.command_id,
                decision_id=command.decision_id,
                executed_by=self.executor_id,
                block_reason="Responsibility contract missing",
                metadata={"check_failed": "responsibility_contract"},
            )
        
        # Execute with responsibility context
        # ...
```

---

## 7. Audit Trail

### 7.1 What is Logged

Every execution includes responsibility metadata:

```json
{
  "execution": {
    "result_id": "result_abc123",
    "command_id": "cmd_xyz789",
    "decision_id": "dec_12345",
    "execution_status": "success"
  },
  "responsibility": {
    "contract_id": "resp_claims_ops_kw",
    "responsible_system": "claims_processing_system",
    "responsible_team": "claims_operations_kuwait",
    "operational_owner": "ops_manager_kw",
    "sla_class": "high",
    "escalation_contact": "escalation@gigkuwait.com"
  }
}
```

### 7.2 Audit Record Method

```python
contract.to_audit_record()
# Returns:
{
    "contract_id": "resp_claims_ops_kw",
    "responsible_system": "claims_processing_system",
    "responsible_team": "claims_operations_kuwait",
    "operational_owner": "ops_manager_kw",
    "sla_class": "high",
    "escalation_contact": "escalation@gigkuwait.com",
}
```

---

## 8. Escalation

### 8.1 When to Escalate

Escalate when:
- ❌ Execution fails
- ❌ SLA violated
- ❌ System unavailable
- ❌ Operational issue detected

### 8.2 Escalation Process

```python
if execution_result.execution_status == ExecutionStatus.FAILED:
    # Escalate to operational owner
    escalate_to = responsibility.escalation_contact
    
    send_escalation(
        to=escalate_to,
        subject=f"Execution Failed: {command.decision_id}",
        body=f"""
        Decision execution failed:
        
        Decision ID: {command.decision_id}
        Command ID: {command.command_id}
        Responsible System: {responsibility.responsible_system}
        Operational Owner: {responsibility.operational_owner}
        SLA Class: {responsibility.sla_class.value}
        
        Failure Reason: {execution_result.failure_reason}
        
        Please investigate immediately.
        """,
    )
```

---

## 9. Examples

### 9.1 Claims Processing

```python
claims_responsibility = create_responsibility_contract(
    responsible_system="claims_processing_system",
    responsible_team="claims_operations_kuwait",
    operational_owner="ops_manager_kw",
    sla_class=SLAClass.HIGH,
    escalation_contact="escalation@gigkuwait.com",
)
```

### 9.2 Fraud Detection

```python
fraud_responsibility = create_responsibility_contract(
    responsible_system="fraud_detection_system",
    responsible_team="fraud_prevention_team",
    operational_owner="fraud_ops_lead",
    sla_class=SLAClass.CRITICAL,
    escalation_contact="fraud-escalation@gigkuwait.com",
)
```

### 9.3 Reporting

```python
reporting_responsibility = create_responsibility_contract(
    responsible_system="reporting_system",
    responsible_team="data_analytics_team",
    operational_owner="analytics_lead",
    sla_class=SLAClass.BEST_EFFORT,
    escalation_contact="analytics@gigkuwait.com",
)
```

---

## 10. Best Practices

### 10.1 Contract Design

1. ✅ One contract per system/service
2. ✅ Clear operational owner
3. ✅ Appropriate SLA class
4. ✅ Valid escalation contact
5. ✅ Team alignment

### 10.2 Operational Ownership

1. ✅ Operational owner should be on-call
2. ✅ Escalation contact should be monitored 24/7
3. ✅ Team should have runbooks for failures
4. ✅ SLA should match business criticality

### 10.3 Monitoring

1. ✅ Track execution success rate per contract
2. ✅ Monitor SLA compliance
3. ✅ Alert on repeated failures
4. ✅ Review contracts quarterly

---

## 11. Conclusion

The Responsibility Contract provides:

1. **Clear Operational Ownership** - Who operates the system
2. **Separation of Concerns** - Authority ≠ Responsibility
3. **SLA Definition** - Clear performance expectations
4. **Escalation Path** - Who to contact on failure
5. **Audit Trail** - Complete operational accountability

This model enables the platform to truthfully state:

> **"Every production execution has clear operational responsibility. If execution fails, we know exactly who is responsible and who to escalate to."**

---

**Document Control:**
- Version: 1.0
- Status: Production-Ready
- Next Review: Q2 2026
- Owner: Platform Operations Team
- Approver: VP of Engineering
