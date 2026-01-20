"""
FNOL Triage Models

Data models for FNOL triage input and output.

Converted to Pydantic for platform standardization.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class TriageCategory(str, Enum):
    """Triage category based on risk score"""
    GREEN = "green"  # Low risk - Standard processing
    YELLOW = "yellow"  # Medium risk - Additional review recommended
    RED = "red"  # High risk - Immediate investigation required


class CustomerInfo(BaseModel):
    """Customer information for triage"""
    customer_id: str = Field(..., description="Unique customer identifier")
    age: int = Field(..., ge=0, le=120, description="Customer age")
    name: Optional[str] = Field(None, description="Customer name")
    email: Optional[str] = Field(None, description="Customer email")
    phone: Optional[str] = Field(None, description="Customer phone number")
    previous_claims: int = Field(default=0, ge=0, description="Number of previous claims")


class PolicyInfo(BaseModel):
    """Policy information for triage"""
    policy_id: str = Field(..., description="Unique policy identifier")
    product_type: str = Field(..., description="Policy product type (motor, property, health, etc.)")
    policy_start_date: Optional[datetime] = Field(None, description="Policy start date")
    policy_end_date: Optional[datetime] = Field(None, description="Policy end date")
    premium: Optional[float] = Field(None, ge=0, description="Policy premium amount")
    coverage_amount: Optional[float] = Field(None, ge=0, description="Coverage amount")


class FNOLInput(BaseModel):
    """
    Input data for FNOL triage.
    
    Represents a First Notice of Loss claim submission.
    """
    claim_id: str = Field(..., description="Unique claim identifier")
    customer: CustomerInfo = Field(..., description="Customer information")
    policy: PolicyInfo = Field(..., description="Policy information")
    description: str = Field(..., min_length=1, description="Claim description")
    estimated_cost: float = Field(..., ge=0, description="Estimated claim cost")
    incident_date: Optional[datetime] = Field(None, description="Date of incident")
    reported_date: Optional[datetime] = Field(None, description="Date claim was reported")
    location: Optional[str] = Field(None, description="Location of incident")
    
    class Config:
        json_schema_extra = {
            "example": {
                "claim_id": "CLM-2026-001",
                "customer": {
                    "customer_id": "CUST-12345",
                    "age": 28,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "previous_claims": 1
                },
                "policy": {
                    "policy_id": "POL-98765",
                    "product_type": "motor",
                    "premium": 1200.00,
                    "coverage_amount": 50000.00
                },
                "description": "Minor fender bender in parking lot",
                "estimated_cost": 1500.00,
                "location": "Seattle, WA"
            }
        }


class TriageRule(BaseModel):
    """Information about a triggered triage rule"""
    rule_name: str = Field(..., description="Name of the rule")
    description: str = Field(..., description="Description of what the rule checks")
    points: int = Field(..., description="Points added if rule is triggered")
    triggered: bool = Field(..., description="Whether the rule was triggered")


class FNOLOutput(BaseModel):
    """
    Output data for FNOL triage.
    
    Contains risk score, category, recommendation, and explanation.
    This is the standardized output format that matches the platform template.
    """
    # Standard platform fields
    decision_id: Optional[str] = Field(None, description="Unique decision identifier")
    timestamp: Optional[datetime] = Field(None, description="Decision timestamp")
    recommendation: str = Field(..., description="Primary recommendation (priority level)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (normalized from risk score)")
    reasoning: str = Field(..., description="Human-readable explanation of the triage decision")
    alternatives: List[str] = Field(default_factory=list, description="Alternative triage categories")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional triage metadata")
    
    # Human-in-the-loop fields
    requires_adjuster_review: bool = Field(default=False, description="Whether adjuster review is required")
    review_reason: Optional[str] = Field(None, description="Reason for requiring review")
    
    # Audit fields
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    model_version: str = Field(default="1.0.0", description="Model version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": "medium_priority",
                "confidence": 0.75,
                "reasoning": "Claim scored 35 points. Triggered rules: motor_product, high_cost. Requires additional review.",
                "alternatives": ["low_priority", "high_priority"],
                "metadata": {
                    "claim_id": "CLM-2026-001",
                    "score": 35,
                    "category": "yellow",
                    "risk_level": "Medium risk - Additional review recommended",
                    "applied_rules": ["motor_product", "high_cost"],
                    "estimated_processing_time": "3-5 business days",
                    "next_steps": [
                        "Assign to experienced adjuster",
                        "Verify all claim details"
                    ]
                }
            }
        }


class FNOLResult(BaseModel):
    """
    Legacy result format for FNOL triage.
    
    Contains risk score, category, and explanation.
    This is maintained for backward compatibility with existing engine.
    """
    claim_id: str = Field(..., description="Claim identifier")
    score: int = Field(..., ge=0, description="Risk score (0-100)")
    category: TriageCategory = Field(..., description="Triage category")
    risk_level: str = Field(..., description="Human-readable risk level")
    applied_rules: List[str] = Field(default_factory=list, description="Names of triggered rules")
    rule_details: List[TriageRule] = Field(default_factory=list, description="Detailed rule information")
    recommendation: str = Field(..., description="Recommendation text")
    priority: str = Field(..., description="Priority level (low, medium, high)")
    estimated_processing_time: str = Field(..., description="Estimated processing time")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    
    def format_summary(self) -> str:
        """Format a human-readable summary"""
        summary = f"\n## FNOL Triage Result\n\n"
        summary += f"**Claim ID**: {self.claim_id}\n"
        summary += f"**Risk Score**: {self.score}/100\n"
        summary += f"**Category**: {self.category.value.upper()}\n"
        summary += f"**Risk Level**: {self.risk_level}\n"
        summary += f"**Priority**: {self.priority.upper()}\n\n"
        
        summary += f"### Applied Rules\n\n"
        for rule in self.rule_details:
            if rule.triggered:
                summary += f"- **{rule.rule_name}** (+{rule.points} points): {rule.description}\n"
        
        summary += f"\n### Recommendation\n\n{self.recommendation}\n\n"
        
        summary += f"### Next Steps\n\n"
        for i, step in enumerate(self.next_steps, 1):
            summary += f"{i}. {step}\n"
        
        summary += f"\n**Estimated Processing Time**: {self.estimated_processing_time}\n"
        
        return summary
    
    def to_output(self) -> FNOLOutput:
        """
        Convert legacy FNOLResult to standardized FNOLOutput format.
        
        This enables integration with core platform services.
        """
        # Normalize score to confidence (0-100 -> 0.0-1.0, inverted for risk)
        # Higher risk score = lower confidence in standard processing
        confidence = 1.0 - (self.score / 100.0)
        
        # Build reasoning from applied rules
        reasoning_parts = [
            f"Claim scored {self.score} points.",
            f"Category: {self.category.value.upper()} - {self.risk_level}."
        ]
        
        if self.applied_rules:
            rules_text = ", ".join(self.applied_rules)
            reasoning_parts.append(f"Triggered rules: {rules_text}.")
        
        reasoning_parts.append(self.recommendation)
        reasoning = " ".join(reasoning_parts)
        
        # Determine alternatives based on category
        alternatives = []
        if self.category == TriageCategory.GREEN:
            alternatives = ["medium_priority", "high_priority"]
        elif self.category == TriageCategory.YELLOW:
            alternatives = ["low_priority", "high_priority"]
        else:  # RED
            alternatives = ["low_priority", "medium_priority"]
        
        # Build metadata with all additional information
        metadata = {
            "claim_id": self.claim_id,
            "score": self.score,
            "category": self.category.value,
            "risk_level": self.risk_level,
            "applied_rules": self.applied_rules,
            "rule_details": [
                {
                    "rule_name": r.rule_name,
                    "description": r.description,
                    "points": r.points,
                    "triggered": r.triggered
                }
                for r in self.rule_details
            ],
            "estimated_processing_time": self.estimated_processing_time,
            "next_steps": self.next_steps
        }
        
        return FNOLOutput(
            recommendation=f"{self.priority}_priority",
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            metadata=metadata
        )
