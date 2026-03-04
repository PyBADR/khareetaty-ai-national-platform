"""
Decision Engine Models

Data models for decision orchestration.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class DecisionType(str, Enum):
    """Types of decisions supported by the platform."""
    
    ADVISORY = "advisory"  # System recommends, human decides
    BOUNDED = "bounded"    # Automated within constraints, escalates exceptions
    SIMULATION = "simulation"  # What-if analysis, no real-world impact


class DecisionContext(BaseModel):
    """Context information for a decision."""
    
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_role: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "adjuster@example.com",
                "user_role": "adjuster",
                "timestamp": "2026-01-20T01:30:00Z",
                "session_id": "sess_123",
                "metadata": {"department": "claims"}
            }
        }


class DecisionResult(BaseModel):
    """Result of a decision execution."""
    
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType
    recommendation: Any
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    alternatives: List[Any] = Field(default_factory=list)
    requires_approval: bool = False
    approval_level: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_123",
                "decision_type": "advisory",
                "recommendation": "standard_priority",
                "confidence": 0.82,
                "reasoning": "Moderate severity, no fraud indicators",
                "alternatives": ["high_priority", "low_priority"],
                "requires_approval": True,
                "approval_level": 2
            }
        }


class Decision(BaseModel):
    """Complete decision record."""
    
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType
    context: DecisionContext
    input_data: Dict[str, Any]
    result: Optional[DecisionResult] = None
    status: str = "pending"  # pending, approved, rejected, executed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "dec_123",
                "decision_type": "advisory",
                "context": {"user_id": "user@example.com", "user_role": "adjuster"},
                "input_data": {"claim_id": "CLM-001", "severity": 6},
                "status": "pending"
            }
        }
