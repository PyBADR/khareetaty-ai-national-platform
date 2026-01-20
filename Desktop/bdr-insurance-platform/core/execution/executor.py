"""
Phase 2.3: Decision Executor

Implements the execution layer with responsibility contracts.
Separates authority (who can decide) from responsibility (who operates it).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from .command import DecisionCommand, ExecutionEnvironment
from .result import ExecutionResult, ExecutionStatus, create_execution_result, create_blocked_result
from .state_machine import DecisionStateMachine, DecisionState


class SLAClass(str, Enum):
    """Service Level Agreement classification"""
    CRITICAL = "critical"        # < 1 minute response
    HIGH = "high"                # < 5 minutes response
    MEDIUM = "medium"            # < 30 minutes response
    LOW = "low"                  # < 4 hours response
    BEST_EFFORT = "best_effort"  # No SLA guarantee


@dataclass(frozen=True)
class ResponsibilityContract:
    """
    Defines operational responsibility for decision execution.
    
    This is SEPARATE from authority:
    - Authority = who can decide
    - Responsibility = who operates/maintains it
    
    Both are required for production execution.
    """
    contract_id: str
    responsible_system: str        # System/service responsible for execution
    responsible_team: str          # Team responsible for operations
    operational_owner: str         # Individual operational owner
    sla_class: SLAClass           # SLA commitment
    escalation_contact: str        # Who to contact if execution fails
    
    def __post_init__(self):
        """Validate responsibility contract"""
        if not self.contract_id:
            raise ValueError("contract_id is required")
        if not self.responsible_system:
            raise ValueError("responsible_system is required")
        if not self.responsible_team:
            raise ValueError("responsible_team is required")
        if not self.operational_owner:
            raise ValueError("operational_owner is required")
        if not self.escalation_contact:
            raise ValueError("escalation_contact is required")
    
    def to_audit_record(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "responsible_system": self.responsible_system,
            "responsible_team": self.responsible_team,
            "operational_owner": self.operational_owner,
            "sla_class": self.sla_class.value,
            "escalation_contact": self.escalation_contact,
        }


@dataclass
class DecisionExecutor:
    """
    Executes decisions with full enforcement and audit trail.
    
    Responsibilities:
    1. Validate execution authority
    2. Validate responsibility contract
    3. Check state machine (must be APPROVED)
    4. Execute decision
    5. Record result
    6. Update state machine
    """
    executor_id: str
    executor_name: str
    
    def execute(
        self,
        command: DecisionCommand,
        state_machine: DecisionStateMachine,
        responsibility: ResponsibilityContract,
        authority_validated: bool = False,
    ) -> ExecutionResult:
        """
        Execute a decision command.
        
        Args:
            command: Decision command to execute
            state_machine: Decision state machine
            responsibility: Responsibility contract
            authority_validated: Whether authority has been validated
        
        Returns:
            ExecutionResult (success or blocked)
        
        Raises:
            Does not raise - returns BLOCKED result instead
        """
        start_time = datetime.now()
        
        # Check 1: Authority must be validated
        if not authority_validated:
            return create_blocked_result(
                command_id=command.command_id,
                decision_id=command.decision_id,
                executed_by=self.executor_id,
                block_reason="Execution authority not validated",
                metadata={"check_failed": "authority_validation"},
            )
        
        # Check 2: State machine must allow execution
        if not state_machine.can_execute():
            return create_blocked_result(
                command_id=command.command_id,
                decision_id=command.decision_id,
                executed_by=self.executor_id,
                block_reason=f"Decision state {state_machine.current_state.value} does not allow execution. Must be APPROVED.",
                metadata={
                    "check_failed": "state_machine",
                    "current_state": state_machine.current_state.value,
                },
            )
        
        # Check 3: Responsibility contract must be present
        if not responsibility:
            return create_blocked_result(
                command_id=command.command_id,
                decision_id=command.decision_id,
                executed_by=self.executor_id,
                block_reason="Responsibility contract missing",
                metadata={"check_failed": "responsibility_contract"},
            )
        
        # Execute decision (placeholder - actual execution logic would go here)
        try:
            # Simulate execution
            execution_successful = self._perform_execution(command, responsibility)
            
            if execution_successful:
                # Update state machine to EXECUTED
                state_machine.transition_to(
                    target_state=DecisionState.EXECUTED,
                    transitioned_by=self.executor_id,
                    reason=f"Executed by {self.executor_name}",
                )
                
                # Calculate duration
                duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return create_execution_result(
                    command_id=command.command_id,
                    decision_id=command.decision_id,
                    execution_status=ExecutionStatus.SUCCESS,
                    executed_by=self.executor_id,
                    execution_duration_ms=duration_ms,
                    metadata={
                        "executor_name": self.executor_name,
                        "responsibility_contract": responsibility.contract_id,
                        "execution_target": command.execution_target.value,
                    },
                )
            else:
                return create_execution_result(
                    command_id=command.command_id,
                    decision_id=command.decision_id,
                    execution_status=ExecutionStatus.FAILED,
                    executed_by=self.executor_id,
                    failure_reason="Execution failed - see logs for details",
                    metadata={"executor_name": self.executor_name},
                )
        
        except Exception as e:
            return create_execution_result(
                command_id=command.command_id,
                decision_id=command.decision_id,
                execution_status=ExecutionStatus.FAILED,
                executed_by=self.executor_id,
                failure_reason=f"Execution exception: {str(e)}",
                metadata={"executor_name": self.executor_name, "exception_type": type(e).__name__},
            )
    
    def _perform_execution(
        self,
        command: DecisionCommand,
        responsibility: ResponsibilityContract,
    ) -> bool:
        """
        Perform actual execution (placeholder).
        
        In production, this would:
        - Call external APIs
        - Update databases
        - Trigger workflows
        - Send notifications
        
        Returns:
            True if execution successful, False otherwise
        """
        # Placeholder - actual execution logic would be implemented here
        # based on command.execution_target
        return True


def execute_decision(
    command: DecisionCommand,
    state_machine: DecisionStateMachine,
    responsibility: ResponsibilityContract,
    executor_id: str = "system_executor",
    executor_name: str = "System Executor",
    authority_validated: bool = False,
) -> ExecutionResult:
    """
    Helper function to execute a decision.
    
    Args:
        command: Decision command
        state_machine: Decision state machine
        responsibility: Responsibility contract
        executor_id: Executor ID
        executor_name: Executor name
        authority_validated: Whether authority has been validated
    
    Returns:
        ExecutionResult
    """
    executor = DecisionExecutor(
        executor_id=executor_id,
        executor_name=executor_name,
    )
    
    return executor.execute(
        command=command,
        state_machine=state_machine,
        responsibility=responsibility,
        authority_validated=authority_validated,
    )


def create_responsibility_contract(
    responsible_system: str,
    responsible_team: str,
    operational_owner: str,
    sla_class: SLAClass,
    escalation_contact: str,
) -> ResponsibilityContract:
    """
    Helper function to create a responsibility contract.
    
    Args:
        responsible_system: System responsible for execution
        responsible_team: Team responsible for operations
        operational_owner: Individual operational owner
        sla_class: SLA classification
        escalation_contact: Escalation contact
    
    Returns:
        ResponsibilityContract
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
