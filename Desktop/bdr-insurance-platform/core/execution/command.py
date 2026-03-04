"""
Phase 2.3: Decision Command

A DecisionCommand represents an explicit request to EXECUTE a decision.
This is separate from the decision itself.

Key Principle:
- Decisions are made (DecisionResponse)
- Decisions are executed (DecisionCommand → ExecutionResult)
- These are separate, auditable steps
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class ExecutionTarget(str, Enum):
    """Where the decision will be executed"""
    SYSTEM = "system"              # Automated system execution
    WORKFLOW = "workflow"          # Human workflow / task assignment
    API = "api"                    # External API call
    SIMULATION = "simulation"      # Simulation only (no real effect)
    DATABASE = "database"          # Database update
    NOTIFICATION = "notification"  # Send notification only


class ExecutionEnvironment(str, Enum):
    """Execution environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DEMO = "demo"                  # Hugging Face Spaces, demos
    SIMULATION = "simulation"      # Pure simulation


@dataclass(frozen=True)
class DecisionCommand:
    """
    Immutable command to execute a decision.
    
    This is NOT the decision itself - it's a request to operationalize it.
    
    Rules:
    - Must reference a valid decision_id
    - Must specify execution target
    - Must specify environment
    - Must identify who requested execution
    - Immutable after creation
    """
    command_id: str
    decision_id: str
    decision_type: str
    execution_target: ExecutionTarget
    environment: ExecutionEnvironment
    requested_by: str              # Authority ID who requested execution
    requested_at: datetime
    execution_parameters: dict     # Target-specific parameters
    
    def __post_init__(self):
        """Validate command on creation"""
        if not self.command_id:
            raise ValueError("command_id is required")
        if not self.decision_id:
            raise ValueError("decision_id is required")
        if not self.decision_type:
            raise ValueError("decision_type is required")
        if not self.requested_by:
            raise ValueError("requested_by is required (authority ID)")
        if not self.requested_at.tzinfo:
            raise ValueError("requested_at must be timezone-aware (UTC)")
    
    def is_production_execution(self) -> bool:
        """Check if this is a production execution"""
        return self.environment == ExecutionEnvironment.PRODUCTION
    
    def is_simulation_only(self) -> bool:
        """Check if this is simulation-only"""
        return (
            self.environment == ExecutionEnvironment.SIMULATION or
            self.execution_target == ExecutionTarget.SIMULATION
        )
    
    def requires_production_gate(self) -> bool:
        """Check if production gate enforcement is required"""
        return self.is_production_execution() and not self.is_simulation_only()


def create_execution_command(
    decision_id: str,
    decision_type: str,
    execution_target: ExecutionTarget,
    environment: ExecutionEnvironment,
    requested_by: str,
    execution_parameters: Optional[dict] = None,
) -> DecisionCommand:
    """
    Helper function to create a DecisionCommand.
    
    Args:
        decision_id: ID of the decision to execute
        decision_type: Type of decision (ADVISORY, BOUNDED, AUTOMATED)
        execution_target: Where to execute (SYSTEM, WORKFLOW, API, etc.)
        environment: Execution environment (PRODUCTION, STAGING, etc.)
        requested_by: Authority ID requesting execution
        execution_parameters: Target-specific parameters
    
    Returns:
        Immutable DecisionCommand
    
    Example:
        >>> cmd = create_execution_command(
        ...     decision_id="dec_12345",
        ...     decision_type="BOUNDED",
        ...     execution_target=ExecutionTarget.SYSTEM,
        ...     environment=ExecutionEnvironment.PRODUCTION,
        ...     requested_by="auth_claims_manager_kw",
        ... )
    """
    return DecisionCommand(
        command_id=f"cmd_{uuid.uuid4().hex[:12]}",
        decision_id=decision_id,
        decision_type=decision_type,
        execution_target=execution_target,
        environment=environment,
        requested_by=requested_by,
        requested_at=datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None),
        execution_parameters=execution_parameters or {},
    )
