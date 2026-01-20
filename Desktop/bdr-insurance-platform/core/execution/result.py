"""
Phase 2.3: Execution Result

ExecutionResult represents the outcome of attempting to execute a decision.
This is immutable and includes a cryptographic hash for audit verification.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import hashlib
import json


class ExecutionStatus(str, Enum):
    """Execution outcome status"""
    SUCCESS = "success"              # Execution completed successfully
    FAILED = "failed"                # Execution attempted but failed
    BLOCKED = "blocked"              # Execution blocked by enforcement
    PENDING = "pending"              # Execution queued but not started
    TIMEOUT = "timeout"              # Execution timed out
    CANCELLED = "cancelled"          # Execution cancelled by authority


@dataclass(frozen=True)
class ExecutionResult:
    """
    Immutable record of decision execution outcome.
    
    Rules:
    - Created after every execution attempt (success or failure)
    - Includes cryptographic hash for tamper detection
    - Logged to audit trail
    - Cannot be modified after creation
    """
    result_id: str
    command_id: str
    decision_id: str
    execution_status: ExecutionStatus
    executed_by: str                    # System/service that executed
    execution_time: datetime
    failure_reason: Optional[str]       # Required if status is FAILED or BLOCKED
    execution_duration_ms: Optional[int]
    result_hash: str                    # Immutable hash for verification
    metadata: dict                      # Additional execution metadata
    
    def __post_init__(self):
        """Validate result on creation"""
        if not self.result_id:
            raise ValueError("result_id is required")
        if not self.command_id:
            raise ValueError("command_id is required")
        if not self.decision_id:
            raise ValueError("decision_id is required")
        if not self.executed_by:
            raise ValueError("executed_by is required")
        if not self.execution_time.tzinfo:
            raise ValueError("execution_time must be timezone-aware (UTC)")
        
        # Validate failure_reason is present for failed/blocked executions
        if self.execution_status in [ExecutionStatus.FAILED, ExecutionStatus.BLOCKED]:
            if not self.failure_reason:
                raise ValueError(f"failure_reason required for status {self.execution_status}")
        
        # Verify hash integrity
        expected_hash = self._compute_hash()
        if self.result_hash != expected_hash:
            raise ValueError("result_hash does not match computed hash - possible tampering")
    
    def _compute_hash(self) -> str:
        """Compute cryptographic hash of execution result"""
        # Create deterministic representation
        hash_data = {
            "result_id": self.result_id,
            "command_id": self.command_id,
            "decision_id": self.decision_id,
            "execution_status": self.execution_status.value,
            "executed_by": self.executed_by,
            "execution_time": self.execution_time.isoformat(),
            "failure_reason": self.failure_reason,
        }
        
        # Compute SHA-256 hash
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def is_successful(self) -> bool:
        """Check if execution was successful"""
        return self.execution_status == ExecutionStatus.SUCCESS
    
    def was_blocked(self) -> bool:
        """Check if execution was blocked by enforcement"""
        return self.execution_status == ExecutionStatus.BLOCKED
    
    def to_audit_record(self) -> dict:
        """Convert to audit record format"""
        return {
            "result_id": self.result_id,
            "command_id": self.command_id,
            "decision_id": self.decision_id,
            "execution_status": self.execution_status.value,
            "executed_by": self.executed_by,
            "execution_time": self.execution_time.isoformat(),
            "failure_reason": self.failure_reason,
            "execution_duration_ms": self.execution_duration_ms,
            "result_hash": self.result_hash,
            "metadata": self.metadata,
        }


def create_execution_result(
    command_id: str,
    decision_id: str,
    execution_status: ExecutionStatus,
    executed_by: str,
    failure_reason: Optional[str] = None,
    execution_duration_ms: Optional[int] = None,
    metadata: Optional[dict] = None,
) -> ExecutionResult:
    """
    Helper function to create an ExecutionResult with automatic hash generation.
    
    Args:
        command_id: ID of the command that was executed
        decision_id: ID of the decision
        execution_status: Outcome status
        executed_by: System/service that executed
        failure_reason: Reason for failure (required if FAILED or BLOCKED)
        execution_duration_ms: Execution duration in milliseconds
        metadata: Additional metadata
    
    Returns:
        Immutable ExecutionResult with cryptographic hash
    """
    import uuid
    from datetime import datetime, timezone
    
    result_id = f"result_{uuid.uuid4().hex[:12]}"
    execution_time = datetime.now(timezone.utc)
    
    # Create temporary result to compute hash
    temp_result = ExecutionResult(
        result_id=result_id,
        command_id=command_id,
        decision_id=decision_id,
        execution_status=execution_status,
        executed_by=executed_by,
        execution_time=execution_time,
        failure_reason=failure_reason,
        execution_duration_ms=execution_duration_ms,
        result_hash="",  # Placeholder
        metadata=metadata or {},
    )
    
    # Compute actual hash
    result_hash = temp_result._compute_hash()
    
    # Create final result with correct hash
    return ExecutionResult(
        result_id=result_id,
        command_id=command_id,
        decision_id=decision_id,
        execution_status=execution_status,
        executed_by=executed_by,
        execution_time=execution_time,
        failure_reason=failure_reason,
        execution_duration_ms=execution_duration_ms,
        result_hash=result_hash,
        metadata=metadata or {},
    )


def create_blocked_result(
    command_id: str,
    decision_id: str,
    executed_by: str,
    block_reason: str,
    metadata: Optional[dict] = None,
) -> ExecutionResult:
    """
    Helper function to create a BLOCKED execution result.
    
    Args:
        command_id: ID of the command that was blocked
        decision_id: ID of the decision
        executed_by: System/service that attempted execution
        block_reason: Reason for blocking
        metadata: Additional metadata
    
    Returns:
        ExecutionResult with BLOCKED status
    """
    return create_execution_result(
        command_id=command_id,
        decision_id=decision_id,
        execution_status=ExecutionStatus.BLOCKED,
        executed_by=executed_by,
        failure_reason=block_reason,
        metadata=metadata,
    )
