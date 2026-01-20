"""
Phase 2.3: Execution Layer Tests

Comprehensive tests for decision execution, state machine, and enforcement.
"""

import pytest
from datetime import datetime, timezone, timedelta

from .command import (
    DecisionCommand,
    ExecutionTarget,
    ExecutionEnvironment,
    create_execution_command,
)
from .result import (
    ExecutionResult,
    ExecutionStatus,
    create_execution_result,
    create_blocked_result,
)
from .state_machine import (
    DecisionState,
    DecisionStateMachine,
    StateTransitionError,
    IllegalStateTransition,
    FinalityViolation,
    create_state_machine,
)
from .executor import (
    DecisionExecutor,
    ResponsibilityContract,
    SLAClass,
    execute_decision,
    create_responsibility_contract,
)
from .enforcement import (
    ExecutionViolation,
    HuggingFaceTrustBoundaryViolation,
    enforce_execution_boundary,
    enforce_hf_trust_boundary,
    validate_execution_authority,
)


# ============================================================================
# Test 1: Decision Command Creation
# ============================================================================

def test_create_decision_command():
    """Test creating a decision command"""
    cmd = create_execution_command(
        decision_id="dec_12345",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.SYSTEM,
        environment=ExecutionEnvironment.PRODUCTION,
        requested_by="auth_manager_kw",
    )
    
    assert cmd.decision_id == "dec_12345"
    assert cmd.execution_target == ExecutionTarget.SYSTEM
    assert cmd.environment == ExecutionEnvironment.PRODUCTION
    assert cmd.is_production_execution()
    assert not cmd.is_simulation_only()
    assert cmd.requires_production_gate()


def test_simulation_command():
    """Test simulation-only command"""
    cmd = create_execution_command(
        decision_id="dec_sim_001",
        decision_type="SIMULATION",
        execution_target=ExecutionTarget.SIMULATION,
        environment=ExecutionEnvironment.DEMO,
        requested_by="demo_user",
    )
    
    assert cmd.is_simulation_only()
    assert not cmd.requires_production_gate()


# ============================================================================
# Test 2: Execution Result with Hash Verification
# ============================================================================

def test_create_execution_result_success():
    """Test creating successful execution result"""
    result = create_execution_result(
        command_id="cmd_abc123",
        decision_id="dec_12345",
        execution_status=ExecutionStatus.SUCCESS,
        executed_by="system_executor",
        execution_duration_ms=150,
    )
    
    assert result.is_successful()
    assert not result.was_blocked()
    assert result.result_hash  # Hash should be generated
    assert len(result.result_hash) == 64  # SHA-256 hash length


def test_create_blocked_result():
    """Test creating blocked execution result"""
    result = create_blocked_result(
        command_id="cmd_blocked",
        decision_id="dec_blocked",
        executed_by="system_executor",
        block_reason="Authority validation failed",
    )
    
    assert result.was_blocked()
    assert not result.is_successful()
    assert result.failure_reason == "Authority validation failed"


# ============================================================================
# Test 3: State Machine - Legal Transitions
# ============================================================================

def test_state_machine_legal_transitions():
    """Test legal state transitions"""
    sm = create_state_machine("dec_12345")
    
    # Initial state
    assert sm.current_state == DecisionState.PROPOSED
    assert not sm.can_execute()
    assert not sm.can_finalize()
    
    # PROPOSED → APPROVED
    sm.transition_to(DecisionState.APPROVED, "approver_001")
    assert sm.current_state == DecisionState.APPROVED
    assert sm.can_execute()
    assert not sm.can_finalize()
    
    # APPROVED → EXECUTED
    sm.transition_to(DecisionState.EXECUTED, "executor_001")
    assert sm.current_state == DecisionState.EXECUTED
    assert not sm.can_execute()
    assert sm.can_finalize()
    
    # EXECUTED → FINALIZED
    sm.transition_to(DecisionState.FINALIZED, "finalizer_001")
    assert sm.current_state == DecisionState.FINALIZED
    assert sm.is_finalized()
    assert not sm.can_execute()
    assert not sm.can_finalize()


# ============================================================================
# Test 4: State Machine - Illegal Transitions (MUST FAIL)
# ============================================================================

def test_state_machine_illegal_transition_proposed_to_executed():
    """Test illegal transition: PROPOSED → EXECUTED (MUST FAIL)"""
    sm = create_state_machine("dec_illegal_001")
    
    with pytest.raises(IllegalStateTransition) as exc_info:
        sm.transition_to(DecisionState.EXECUTED, "bad_actor")
    
    assert "Illegal state transition" in str(exc_info.value)
    assert "proposed" in str(exc_info.value).lower()
    assert "executed" in str(exc_info.value).lower()


def test_state_machine_illegal_transition_proposed_to_finalized():
    """Test illegal transition: PROPOSED → FINALIZED (MUST FAIL)"""
    sm = create_state_machine("dec_illegal_002")
    
    with pytest.raises(IllegalStateTransition) as exc_info:
        sm.transition_to(DecisionState.FINALIZED, "bad_actor")
    
    assert "Illegal state transition" in str(exc_info.value)


def test_state_machine_finality_violation():
    """Test finality violation: Cannot modify FINALIZED decision (MUST FAIL)"""
    sm = create_state_machine("dec_final_001")
    
    # Transition to FINALIZED
    sm.transition_to(DecisionState.APPROVED, "approver")
    sm.transition_to(DecisionState.EXECUTED, "executor")
    sm.transition_to(DecisionState.FINALIZED, "finalizer")
    
    # Attempt to modify FINALIZED decision
    with pytest.raises(FinalityViolation) as exc_info:
        sm.transition_to(DecisionState.REVOKED, "bad_actor")
    
    assert "FINALIZED" in str(exc_info.value)
    assert "immutable" in str(exc_info.value).lower()


# ============================================================================
# Test 5: Responsibility Contract
# ============================================================================

def test_create_responsibility_contract():
    """Test creating responsibility contract"""
    contract = create_responsibility_contract(
        responsible_system="claims_processing_system",
        responsible_team="claims_operations_kuwait",
        operational_owner="ops_manager_kw",
        sla_class=SLAClass.HIGH,
        escalation_contact="escalation@gigkuwait.com",
    )
    
    assert contract.responsible_system == "claims_processing_system"
    assert contract.sla_class == SLAClass.HIGH
    assert contract.escalation_contact == "escalation@gigkuwait.com"


# ============================================================================
# Test 6: Hugging Face Trust Boundary (MUST BLOCK)
# ============================================================================

def test_hf_trust_boundary_blocks_production_execution():
    """Test HF cannot execute production decisions (MUST BLOCK)"""
    cmd = create_execution_command(
        decision_id="dec_prod_001",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.SYSTEM,
        environment=ExecutionEnvironment.PRODUCTION,
        requested_by="hf_space_user",
    )
    
    with pytest.raises(HuggingFaceTrustBoundaryViolation) as exc_info:
        enforce_hf_trust_boundary(cmd, "huggingface_space_demo")
    
    assert "NON-TRUSTED EXECUTION ZONE" in str(exc_info.value)
    assert "production" in str(exc_info.value).lower()


def test_hf_trust_boundary_blocks_non_simulation():
    """Test HF can only execute simulations (MUST BLOCK)"""
    cmd = create_execution_command(
        decision_id="dec_demo_001",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.API,  # Not simulation
        environment=ExecutionEnvironment.DEMO,
        requested_by="demo_user",
    )
    
    with pytest.raises(HuggingFaceTrustBoundaryViolation) as exc_info:
        enforce_hf_trust_boundary(cmd, "hf_space_claims_demo")
    
    assert "simulation" in str(exc_info.value).lower()
    assert "NON-TRUSTED" in str(exc_info.value)


def test_hf_trust_boundary_allows_simulation():
    """Test HF CAN execute simulations (MUST PASS)"""
    cmd = create_execution_command(
        decision_id="dec_sim_001",
        decision_type="SIMULATION",
        execution_target=ExecutionTarget.SIMULATION,
        environment=ExecutionEnvironment.DEMO,
        requested_by="demo_user",
    )
    
    # Should not raise exception
    enforce_hf_trust_boundary(cmd, "huggingface_space_demo")


# ============================================================================
# Test 7: Execution Enforcement
# ============================================================================

def test_execution_requires_approved_state():
    """Test execution requires APPROVED state (MUST BLOCK if not approved)"""
    sm = create_state_machine("dec_not_approved")
    # State is PROPOSED, not APPROVED
    
    cmd = create_execution_command(
        decision_id="dec_not_approved",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.SYSTEM,
        environment=ExecutionEnvironment.STAGING,
        requested_by="auth_001",
    )
    
    responsibility = create_responsibility_contract(
        responsible_system="test_system",
        responsible_team="test_team",
        operational_owner="test_owner",
        sla_class=SLAClass.MEDIUM,
        escalation_contact="test@example.com",
    )
    
    with pytest.raises(ExecutionViolation) as exc_info:
        enforce_execution_boundary(
            command=cmd,
            state_machine=sm,
            authority=None,
            authority_anchor=None,
            responsibility=responsibility,
            requesting_system="test_system",
        )
    
    assert "APPROVED" in str(exc_info.value)


# ============================================================================
# Test 8: Decision Executor
# ============================================================================

def test_executor_blocks_without_authority():
    """Test executor blocks execution without authority validation"""
    sm = create_state_machine("dec_exec_001")
    sm.transition_to(DecisionState.APPROVED, "approver")
    
    cmd = create_execution_command(
        decision_id="dec_exec_001",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.SYSTEM,
        environment=ExecutionEnvironment.STAGING,
        requested_by="auth_001",
    )
    
    responsibility = create_responsibility_contract(
        responsible_system="test_system",
        responsible_team="test_team",
        operational_owner="test_owner",
        sla_class=SLAClass.MEDIUM,
        escalation_contact="test@example.com",
    )
    
    executor = DecisionExecutor(
        executor_id="test_executor",
        executor_name="Test Executor",
    )
    
    result = executor.execute(
        command=cmd,
        state_machine=sm,
        responsibility=responsibility,
        authority_validated=False,  # Not validated
    )
    
    assert result.was_blocked()
    assert "authority not validated" in result.failure_reason.lower()


def test_executor_successful_execution():
    """Test successful execution with all requirements met"""
    sm = create_state_machine("dec_exec_success")
    sm.transition_to(DecisionState.APPROVED, "approver")
    
    cmd = create_execution_command(
        decision_id="dec_exec_success",
        decision_type="BOUNDED",
        execution_target=ExecutionTarget.SYSTEM,
        environment=ExecutionEnvironment.STAGING,
        requested_by="auth_001",
    )
    
    responsibility = create_responsibility_contract(
        responsible_system="test_system",
        responsible_team="test_team",
        operational_owner="test_owner",
        sla_class=SLAClass.MEDIUM,
        escalation_contact="test@example.com",
    )
    
    result = execute_decision(
        command=cmd,
        state_machine=sm,
        responsibility=responsibility,
        authority_validated=True,  # Validated
    )
    
    assert result.is_successful()
    assert sm.current_state == DecisionState.EXECUTED


# ============================================================================
# Test 9: Audit Trail
# ============================================================================

def test_state_machine_audit_trail():
    """Test state machine maintains complete audit trail"""
    sm = create_state_machine("dec_audit_001")
    
    sm.transition_to(DecisionState.APPROVED, "approver_001", "Approved by manager")
    sm.transition_to(DecisionState.EXECUTED, "executor_001", "Executed successfully")
    sm.transition_to(DecisionState.FINALIZED, "finalizer_001", "Finalized")
    
    history = sm.get_transition_history()
    
    assert len(history) == 3
    assert history[0]["from_state"] == "proposed"
    assert history[0]["to_state"] == "approved"
    assert history[1]["from_state"] == "approved"
    assert history[1]["to_state"] == "executed"
    assert history[2]["from_state"] == "executed"
    assert history[2]["to_state"] == "finalized"


def test_execution_result_audit_record():
    """Test execution result generates audit record"""
    result = create_execution_result(
        command_id="cmd_audit_001",
        decision_id="dec_audit_001",
        execution_status=ExecutionStatus.SUCCESS,
        executed_by="system_executor",
        execution_duration_ms=200,
        metadata={"test": "data"},
    )
    
    audit_record = result.to_audit_record()
    
    assert audit_record["result_id"] == result.result_id
    assert audit_record["execution_status"] == "success"
    assert audit_record["result_hash"] == result.result_hash
    assert audit_record["metadata"]["test"] == "data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
