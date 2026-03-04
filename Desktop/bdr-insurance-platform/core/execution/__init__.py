"""
Phase 2.3: Decision Finality & Execution Boundary

This module implements the execution layer that separates:
- Decision making (what should happen)
- Decision execution (making it happen)
- Decision finality (irreversible commitment)

Key Principles:
1. Decisions DO NOT execute themselves
2. Execution requires explicit authority AND responsibility
3. Finality is irreversible and enforced at runtime
4. Hugging Face Spaces are NON-TRUSTED EXECUTION ZONES
"""

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
)

from .executor import (
    DecisionExecutor,
    ResponsibilityContract,
    SLAClass,
    execute_decision,
)

from .enforcement import (
    ExecutionViolation,
    HuggingFaceTrustBoundaryViolation,
    enforce_execution_boundary,
    enforce_hf_trust_boundary,
    validate_execution_authority,
)

__all__ = [
    # Command
    'DecisionCommand',
    'ExecutionTarget',
    'ExecutionEnvironment',
    'create_execution_command',
    # Result
    'ExecutionResult',
    'ExecutionStatus',
    'create_execution_result',
    'create_blocked_result',
    # State Machine
    'DecisionState',
    'DecisionStateMachine',
    'StateTransitionError',
    'IllegalStateTransition',
    'FinalityViolation',
    # Executor
    'DecisionExecutor',
    'ResponsibilityContract',
    'SLAClass',
    'execute_decision',
    # Enforcement
    'ExecutionViolation',
    'HuggingFaceTrustBoundaryViolation',
    'enforce_execution_boundary',
    'enforce_hf_trust_boundary',
    'validate_execution_authority',
]
