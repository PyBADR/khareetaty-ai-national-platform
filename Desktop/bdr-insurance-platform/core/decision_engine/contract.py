"""Core Decision Contract - Single Source of Truth.

This contract is the ONLY valid interface for all insurance decisions.
Returning raw dicts is forbidden. All modules MUST use DecisionResponse.

Contract guarantees:
- Single decision shape across all products
- Mandatory human-in-the-loop enforcement
- Complete explainability
- Full audit trail
- Boundary checking
"""

from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4

from .enums import DecisionType
from .boundaries import BoundaryResult
from .explainability import Explainability

if TYPE_CHECKING:
    from .position import DecisionPosition
    from core.governance import AccountabilityChain, AccountabilityScope


class DecisionRequest(BaseModel):
    """Standard request format for all decision modules.
    
    Attributes:
        decision_id: Unique identifier for this decision (auto-generated if not provided)
        decision_type: Type of decision (advisory, bounded, simulation)
        module_name: Name of the module making the decision
        input_data: Module-specific input data
        user_id: ID of the user requesting the decision
        session_id: Optional session ID for tracking
        override_boundaries: Whether to override boundary checks (requires elevated permissions)
        metadata: Additional request metadata
    """
    
    decision_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this decision"
    )
    decision_type: DecisionType = Field(
        ..., description="Type of decision being requested"
    )
    module_name: str = Field(
        ..., description="Name of the module making the decision"
    )
    input_data: Dict[str, Any] = Field(
        ..., description="Module-specific input data"
    )
    user_id: str = Field(
        ..., description="ID of the user requesting the decision"
    )
    session_id: Optional[str] = Field(
        None, description="Optional session ID for tracking"
    )
    override_boundaries: bool = Field(
        default=False,
        description="Whether to override boundary checks (requires elevated permissions)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional request metadata"
    )
    ownership: Optional[Any] = Field(
        None,
        description="Ownership & accountability chain (Phase 2.1 - MANDATORY for production)"
    )
    accountability_scope: Optional[Any] = Field(
        None,
        description="Accountability scope defining allowed actions and limits (Phase 2.1 - MANDATORY for production)"
    )
    
    @field_validator('ownership', 'accountability_scope', mode='before')
    @classmethod
    def validate_ownership_in_production(cls, v, info):
        """Validate ownership is present in production environments.
        
        In production, ownership and accountability_scope are MANDATORY.
        In dev/test, they are optional to allow gradual migration.
        """
        # Get environment from metadata if available
        metadata = info.data.get('metadata', {})
        environment = metadata.get('environment', 'development')
        
        # In production, ownership is MANDATORY
        if environment == 'production' and v is None:
            from core.governance import OwnershipViolation
            raise OwnershipViolation(
                f"Field '{info.field_name}' is MANDATORY in production environment. "
                "All production decisions must have explicit ownership and accountability."
            )
        
        return v
    
    def enforce_ownership_requirements(self) -> None:
        """Enforce ownership and accountability requirements.
        
        This method MUST be called before:
        - Model inference
        - DecisionResponse creation
        - Any decision processing
        
        Raises:
            OwnershipViolation: If ownership requirements are not met
            AccountabilityViolation: If accountability scope is violated
        """
        # Import here to avoid circular dependency
        from core.governance import enforce_ownership
        
        # Enforce ownership requirements
        enforce_ownership(
            decision_request=self,
            ownership=self.ownership,
            scope=self.accountability_scope,
        )
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_123e4567-e89b-12d3-a456-426614174000",
                "decision_type": "bounded",
                "module_name": "fnol_triage",
                "input_data": {
                    "claim_amount": 25000.0,
                    "policy_number": "POL-12345",
                    "incident_description": "Vehicle collision"
                },
                "user_id": "user_789",
                "session_id": "sess_abc123",
                "override_boundaries": False,
                "metadata": {
                    "source": "web_portal",
                    "ip_address": "192.168.1.1"
                }
            }
        }


class AuditMetadata(BaseModel):
    """Mandatory audit metadata for every decision.
    
    Attributes:
        decision_id: Unique identifier for this decision
        timestamp: When the decision was made (ISO 8601)
        module_name: Name of the module that made the decision
        module_version: Version of the module
        user_id: ID of the user who requested the decision
        session_id: Optional session ID
        processing_time_ms: Time taken to process the decision (milliseconds)
        environment: Environment where decision was made (dev/staging/prod)
        audit_trail: Additional audit trail information
    """
    
    decision_id: str = Field(
        ..., description="Unique identifier for this decision"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the decision was made (UTC)"
    )
    module_name: str = Field(
        ..., description="Name of the module that made the decision"
    )
    module_version: str = Field(
        ..., description="Version of the module"
    )
    user_id: str = Field(
        ..., description="ID of the user who requested the decision"
    )
    session_id: Optional[str] = Field(
        None, description="Optional session ID"
    )
    processing_time_ms: int = Field(
        ..., ge=0, description="Processing time in milliseconds"
    )
    environment: str = Field(
        default="production",
        description="Environment where decision was made"
    )
    audit_trail: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional audit trail information"
    )
    ownership_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Ownership and accountability metadata (Phase 2.1)"
    )
    authority_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authority enforcement metadata (Phase 2.1.1)"
    )
    authority_anchor_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Authority anchor metadata for legal attribution (Phase 2.2)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2026-01-20T18:30:00Z",
                "module_name": "fnol_triage",
                "module_version": "1.0.0",
                "user_id": "user_789",
                "session_id": "sess_abc123",
                "processing_time_ms": 145,
                "environment": "production",
                "audit_trail": {
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0",
                    "request_source": "web_portal"
                }
            }
        }


class DecisionResponse(BaseModel):
    """Core Decision Contract - ONLY valid return type for all modules.
    
    This is the single source of truth for decision responses.
    ALL modules MUST return this type. Raw dicts are forbidden.
    
    Attributes:
        decision_id: Unique identifier for this decision
        decision_type: Type of decision (advisory, bounded, simulation)
        decision_output: Module-specific decision output
        boundaries: Boundary check results
        explainability: Mandatory explainability payload
        audit_metadata: Mandatory audit metadata
        position: Decision ownership & liability contract (Phase 2 - MANDATORY)
        human_review_required: Explicit flag for human review requirement
        human_review_reason: Human-readable reason for review (if required)
        actionable: Whether this decision can be acted upon automatically
        errors: Any errors encountered during decision processing
    """
    
    decision_id: str = Field(
        ..., description="Unique identifier for this decision"
    )
    decision_type: DecisionType = Field(
        ..., description="Type of decision"
    )
    decision_output: Dict[str, Any] = Field(
        ..., description="Module-specific decision output"
    )
    boundaries: BoundaryResult = Field(
        ..., description="Boundary check results"
    )
    explainability: Explainability = Field(
        ..., description="Mandatory explainability payload"
    )
    audit_metadata: AuditMetadata = Field(
        ..., description="Mandatory audit metadata"
    )
    position: Optional[Any] = Field(
        None,
        description="Decision ownership & liability contract (Phase 2 - MANDATORY for production)"
    )
    authority_explanation: Optional[Any] = Field(
        None,
        description="Authority explanation for legal attribution (Phase 2.2 - MANDATORY for production)"
    )
    human_review_required: bool = Field(
        ..., description="Explicit flag for human review requirement"
    )
    human_review_reason: Optional[str] = Field(
        None, description="Human-readable reason for review (if required)"
    )
    actionable: bool = Field(
        ..., description="Whether this decision can be acted upon automatically"
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Any errors encountered during decision processing"
    )
    
    def is_actionable(self) -> bool:
        """Check if this decision can result in automated action.
        
        A decision is actionable if and only if:
        1. It is a BOUNDED decision type
        2. All boundary checks passed
        3. No human review is required
        4. No errors occurred
        
        Returns:
            True if the decision can be acted upon automatically.
        """
        return (
            self.decision_type == DecisionType.BOUNDED
            and self.boundaries.all_passed
            and not self.human_review_required
            and len(self.errors) == 0
        )
    
    def get_review_summary(self) -> str:
        """Get a summary of why human review is required (if applicable).
        
        Returns:
            Human-readable summary of review requirements.
        """
        if not self.human_review_required:
            return "No human review required"
        
        reasons = []
        
        if self.decision_type == DecisionType.ADVISORY:
            reasons.append("Advisory decision always requires human review")
        
        if not self.boundaries.all_passed:
            reasons.append(f"Boundary checks failed: {self.boundaries.get_failure_summary()}")
        
        if self.human_review_reason:
            reasons.append(self.human_review_reason)
        
        return "; ".join(reasons) if reasons else "Human review required"
    
    def get_confidence_level(self) -> str:
        """Get a human-readable confidence level.
        
        Returns:
            'high', 'medium', or 'low' based on explainability confidence score.
        """
        score = self.explainability.confidence_score
        if score >= 0.8:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def to_audit_log(self) -> Dict[str, Any]:
        """Convert to audit log format.
        
        Returns:
            Dictionary suitable for audit logging.
        """
        audit_log = {
            "decision_id": self.decision_id,
            "timestamp": self.audit_metadata.timestamp.isoformat(),
            "module": self.audit_metadata.module_name,
            "module_version": self.audit_metadata.module_version,
            "decision_type": self.decision_type.value,
            "user_id": self.audit_metadata.user_id,
            "human_review_required": self.human_review_required,
            "actionable": self.actionable,
            "confidence": self.explainability.confidence_score,
            "processing_time_ms": self.audit_metadata.processing_time_ms,
            "boundaries_passed": self.boundaries.all_passed,
            "errors": self.errors
        }
        
        # Include ownership metadata if present (Phase 2.1)
        if self.audit_metadata.ownership_metadata:
            audit_log["ownership"] = self.audit_metadata.ownership_metadata
        
        # Include authority metadata if present (Phase 2.1.1)
        if self.audit_metadata.authority_metadata:
            audit_log["authority"] = self.audit_metadata.authority_metadata
        
        return audit_log
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_123e4567-e89b-12d3-a456-426614174000",
                "decision_type": "bounded",
                "decision_output": {
                    "priority": "high",
                    "risk_category": "yellow",
                    "recommended_action": "assign_to_adjuster"
                },
                "boundaries": {
                    "checks": [
                        {
                            "boundary_type": "monetary",
                            "name": "High Value Threshold",
                            "threshold": 50000.0,
                            "actual_value": 25000.0,
                            "passed": True,
                            "reason": "Within auto-approval threshold"
                        }
                    ],
                    "all_passed": True,
                    "failed_checks": [],
                    "human_review_reason": None
                },
                "explainability": {
                    "summary": "Standard claim with no red flags, auto-approved",
                    "key_factors": [
                        {
                            "name": "claim_amount",
                            "value": 25000.0,
                            "weight": 0.7,
                            "impact": "neutral",
                            "description": "Claim amount within normal range"
                        }
                    ],
                    "scored_signals": [],
                    "evidence": [],
                    "confidence_score": 0.92,
                    "model_version": "fnol_triage_v1.0.0",
                    "explanation_metadata": {}
                },
                "audit_metadata": {
                    "decision_id": "dec_123e4567-e89b-12d3-a456-426614174000",
                    "timestamp": "2026-01-20T18:30:00Z",
                    "module_name": "fnol_triage",
                    "module_version": "1.0.0",
                    "user_id": "user_789",
                    "session_id": "sess_abc123",
                    "processing_time_ms": 145,
                    "environment": "production",
                    "audit_trail": {}
                },
                "human_review_required": False,
                "human_review_reason": None,
                "actionable": True,
                "errors": []
            }
        }
