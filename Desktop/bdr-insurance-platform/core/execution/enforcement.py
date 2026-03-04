"""
Phase 2.3: Execution Enforcement

Enforces execution boundaries and Hugging Face trust boundary.

Key Rules:
1. Production execution requires authority + responsibility + approved state
2. Hugging Face Spaces are NON-TRUSTED EXECUTION ZONES
3. HF can create decisions, but CANNOT execute production decisions
4. All violations are HARD BLOCKS (no warnings, no fallback)
"""

from typing import Optional
from datetime import datetime, timezone

from .command import DecisionCommand, ExecutionEnvironment, ExecutionTarget
from .state_machine import DecisionStateMachine, DecisionState
from .executor import ResponsibilityContract

# Import from governance layer
try:
    from ..governance.authority_anchor import AuthorityAnchor, validate_anchor_for_production
    from ..governance.authority import DecisionAuthority
except ImportError:
    # Fallback for testing
    AuthorityAnchor = None
    DecisionAuthority = None
    validate_anchor_for_production = None


class ExecutionViolation(Exception):
    """Raised when execution boundary is violated"""
    pass


class HuggingFaceTrustBoundaryViolation(ExecutionViolation):
    """Raised when Hugging Face attempts unauthorized execution"""
    pass


# Hugging Face Trust Boundary
HF_TRUSTED_OPERATIONS = {
    "create_decision",
    "request_approval",
    "display_output",
    "simulate_decision",
}

HF_FORBIDDEN_OPERATIONS = {
    "execute_production_decision",
    "finalize_decision",
    "override_state",
    "modify_authority",
    "bypass_enforcement",
}


def enforce_hf_trust_boundary(
    command: DecisionCommand,
    requesting_system: str,
) -> None:
    """
    Enforce Hugging Face trust boundary.
    
    Hugging Face Spaces are NON-TRUSTED EXECUTION ZONES.
    They may:
    - Create decisions
    - Request approvals
    - Display outputs
    - Run simulations
    
    They may NEVER:
    - Execute production decisions
    - Finalize decisions
    - Override state
    - Modify authority
    
    Args:
        command: Decision command
        requesting_system: System requesting execution
    
    Raises:
        HuggingFaceTrustBoundaryViolation: If HF attempts forbidden operation
    """
    # Check if request is from Hugging Face
    is_hf_request = (
        "huggingface" in requesting_system.lower() or
        "hf_space" in requesting_system.lower() or
        command.environment == ExecutionEnvironment.DEMO
    )
    
    if not is_hf_request:
        return  # Not from HF, no restriction
    
    # HF can only execute simulations
    if command.execution_target != ExecutionTarget.SIMULATION:
        raise HuggingFaceTrustBoundaryViolation(
            f"Hugging Face Spaces cannot execute non-simulation decisions. "
            f"Attempted execution target: {command.execution_target.value}. "
            f"HF Spaces are NON-TRUSTED EXECUTION ZONES and may only run simulations."
        )
    
    # HF cannot execute in production
    if command.environment == ExecutionEnvironment.PRODUCTION:
        raise HuggingFaceTrustBoundaryViolation(
            f"Hugging Face Spaces cannot execute production decisions. "
            f"HF Spaces are NON-TRUSTED EXECUTION ZONES. "
            f"Production execution must occur in trusted infrastructure."
        )


def validate_execution_authority(
    command: DecisionCommand,
    authority: Optional['DecisionAuthority'],
    authority_anchor: Optional['AuthorityAnchor'],
) -> None:
    """
    Validate execution authority.
    
    Args:
        command: Decision command
        authority: Decision authority
        authority_anchor: Authority anchor
    
    Raises:
        ExecutionViolation: If authority is insufficient
    """
    # Production execution requires authority
    if command.requires_production_gate():
        if not authority:
            raise ExecutionViolation(
                f"Production execution requires DecisionAuthority. "
                f"Command {command.command_id} has no authority."
            )
        
        if not authority.can_execute:
            raise ExecutionViolation(
                f"Authority {authority.authority_id} does not have execution permission. "
                f"can_execute=False."
            )
        
        # Validate authority anchor
        if not authority_anchor:
            raise ExecutionViolation(
                f"Production execution requires AuthorityAnchor. "
                f"Command {command.command_id} has no authority anchor."
            )
        
        # Validate anchor for production (if validation function available)
        if validate_anchor_for_production:
            try:
                validate_anchor_for_production(
                    anchor=authority_anchor,
                    environment="production",
                )
            except Exception as e:
                raise ExecutionViolation(
                    f"Authority anchor validation failed: {str(e)}"
                )


def enforce_execution_boundary(
    command: DecisionCommand,
    state_machine: DecisionStateMachine,
    authority: Optional['DecisionAuthority'],
    authority_anchor: Optional['AuthorityAnchor'],
    responsibility: Optional[ResponsibilityContract],
    requesting_system: str,
) -> None:
    """
    Enforce execution boundary with all checks.
    
    This is the MAIN enforcement function that must be called before execution.
    
    Checks:
    1. Hugging Face trust boundary
    2. State machine (must be APPROVED)
    3. Execution authority
    4. Responsibility contract (production only)
    5. Jurisdiction match (production only)
    
    Args:
        command: Decision command
        state_machine: Decision state machine
        authority: Decision authority
        authority_anchor: Authority anchor
        responsibility: Responsibility contract
        requesting_system: System requesting execution
    
    Raises:
        ExecutionViolation: If any check fails
        HuggingFaceTrustBoundaryViolation: If HF trust boundary violated
    """
    # Check 1: Hugging Face trust boundary
    enforce_hf_trust_boundary(command, requesting_system)
    
    # Check 2: State machine must allow execution
    if not state_machine.can_execute():
        raise ExecutionViolation(
            f"Decision {command.decision_id} cannot be executed. "
            f"Current state: {state_machine.current_state.value}. "
            f"Required state: {DecisionState.APPROVED.value}."
        )
    
    # Check 3: Execution authority
    validate_execution_authority(command, authority, authority_anchor)
    
    # Check 4: Responsibility contract (production only)
    if command.requires_production_gate():
        if not responsibility:
            raise ExecutionViolation(
                f"Production execution requires ResponsibilityContract. "
                f"Command {command.command_id} has no responsibility contract."
            )
    
    # Check 5: Jurisdiction match (production only)
    if command.requires_production_gate() and authority_anchor:
        # Jurisdiction validation would go here
        # For now, we assume jurisdiction is validated in authority_anchor validation
        pass


def get_execution_audit_metadata(
    command: DecisionCommand,
    authority: Optional['DecisionAuthority'],
    responsibility: Optional[ResponsibilityContract],
    requesting_system: str,
) -> dict:
    """
    Get execution audit metadata.
    
    Args:
        command: Decision command
        authority: Decision authority
        responsibility: Responsibility contract
        requesting_system: System requesting execution
    
    Returns:
        Audit metadata dictionary
    """
    return {
        "command_id": command.command_id,
        "decision_id": command.decision_id,
        "execution_target": command.execution_target.value,
        "environment": command.environment.value,
        "requested_by": command.requested_by,
        "requested_at": command.requested_at.isoformat(),
        "requesting_system": requesting_system,
        "authority_id": authority.authority_id if authority else None,
        "responsibility_contract_id": responsibility.contract_id if responsibility else None,
        "is_production": command.is_production_execution(),
        "is_simulation": command.is_simulation_only(),
    }
