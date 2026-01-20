"""Policy Engine Models"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PolicyType(str, Enum):
    """Types of policies."""
    REGULATORY = "regulatory"  # Compliance requirements
    BUSINESS = "business"      # Business rules
    OPERATIONAL = "operational"  # SLAs, performance


class Policy(BaseModel):
    """Business rule or constraint definition."""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    rules: Dict[str, Any]
    active: bool = True
    priority: int = 0


class Constraint(BaseModel):
    """Input or output constraint."""
    name: str
    condition: str
    threshold: Any
    message: str


class ValidationResult(BaseModel):
    """Result of policy validation."""
    is_valid: bool
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    policies_checked: List[str] = Field(default_factory=list)
