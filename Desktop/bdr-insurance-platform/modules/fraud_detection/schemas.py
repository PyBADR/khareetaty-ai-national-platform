"""Fraud Detection Module - Input/Output Schemas.

Standardized Pydantic schemas for fraud detection decision intelligence.
Follows platform-wide schema conventions defined in modules/MODULE_TEMPLATE.md
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class FraudRiskLevel(str, Enum):
    """Fraud risk classification levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ClaimType(str, Enum):
    """Insurance claim types."""
    AUTO = "auto"
    PROPERTY = "property"
    HEALTH = "health"
    LIFE = "life"
    LIABILITY = "liability"
    WORKERS_COMP = "workers_comp"


class TransactionPattern(BaseModel):
    """Transaction pattern analysis data."""
    
    frequency_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Frequency anomaly score (0=normal, 1=highly anomalous)"
    )
    amount_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Amount anomaly score (0=normal, 1=highly anomalous)"
    )
    timing_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Timing anomaly score (0=normal, 1=highly anomalous)"
    )
    velocity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Velocity anomaly score (0=normal, 1=highly anomalous)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "frequency_score": 0.75,
                "amount_score": 0.82,
                "timing_score": 0.45,
                "velocity_score": 0.68
            }
        }
    )


class ClaimantHistory(BaseModel):
    """Historical claim information for claimant."""
    
    total_claims: int = Field(
        ...,
        ge=0,
        description="Total number of previous claims"
    )
    claims_last_12_months: int = Field(
        ...,
        ge=0,
        description="Number of claims in last 12 months"
    )
    total_claimed_amount: Decimal = Field(
        ...,
        ge=0,
        description="Total amount claimed historically"
    )
    average_claim_amount: Decimal = Field(
        ...,
        ge=0,
        description="Average claim amount"
    )
    previous_fraud_flags: int = Field(
        default=0,
        ge=0,
        description="Number of previous fraud flags or investigations"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_claims": 5,
                "claims_last_12_months": 2,
                "total_claimed_amount": "45000.00",
                "average_claim_amount": "9000.00",
                "previous_fraud_flags": 0
            }
        }
    )


class FraudInput(BaseModel):
    """Input schema for fraud detection analysis.
    
    Standardized input following platform conventions.
    All fraud detection requests must conform to this schema.
    """
    
    # Claim identification
    claim_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique claim identifier"
    )
    claim_type: ClaimType = Field(
        ...,
        description="Type of insurance claim"
    )
    claim_date: datetime = Field(
        ...,
        description="Date and time claim was filed"
    )
    
    # Claim details
    claimed_amount: Decimal = Field(
        ...,
        ge=0,
        description="Amount claimed in USD"
    )
    incident_date: datetime = Field(
        ...,
        description="Date and time of incident"
    )
    incident_description: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Description of the incident"
    )
    incident_location: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Location where incident occurred"
    )
    
    # Claimant information
    claimant_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique claimant identifier"
    )
    claimant_history: ClaimantHistory = Field(
        ...,
        description="Historical claim data for claimant"
    )
    
    # Policy information
    policy_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Policy identifier"
    )
    policy_start_date: datetime = Field(
        ...,
        description="Policy effective start date"
    )
    policy_premium: Decimal = Field(
        ...,
        ge=0,
        description="Annual policy premium in USD"
    )
    
    # Transaction patterns (optional, computed if available)
    transaction_pattern: Optional[TransactionPattern] = Field(
        default=None,
        description="Transaction pattern analysis (if available)"
    )
    
    # Supporting evidence
    has_police_report: bool = Field(
        default=False,
        description="Whether a police report was filed"
    )
    has_witness_statements: bool = Field(
        default=False,
        description="Whether witness statements are available"
    )
    has_medical_records: bool = Field(
        default=False,
        description="Whether medical records are attached"
    )
    has_photos: bool = Field(
        default=False,
        description="Whether photos/evidence are attached"
    )
    
    # Context
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or metadata"
    )

    @field_validator('incident_date')
    @classmethod
    def incident_before_claim(cls, v: datetime, info) -> datetime:
        """Validate incident occurred before or at claim date."""
        if 'claim_date' in info.data and v > info.data['claim_date']:
            raise ValueError('Incident date cannot be after claim date')
        return v

    @field_validator('policy_start_date')
    @classmethod
    def policy_active_at_incident(cls, v: datetime, info) -> datetime:
        """Validate policy was active at time of incident."""
        if 'incident_date' in info.data and v > info.data['incident_date']:
            raise ValueError('Policy must be active at time of incident')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "claim_id": "CLM-2026-001234",
                "claim_type": "auto",
                "claim_date": "2026-01-15T10:30:00Z",
                "claimed_amount": "15000.00",
                "incident_date": "2026-01-14T18:45:00Z",
                "incident_description": "Vehicle collision at intersection, rear-end impact causing significant damage to rear bumper and trunk.",
                "incident_location": "Main St & 5th Ave, Seattle, WA",
                "claimant_id": "CLMT-789456",
                "claimant_history": {
                    "total_claims": 3,
                    "claims_last_12_months": 1,
                    "total_claimed_amount": "22000.00",
                    "average_claim_amount": "7333.33",
                    "previous_fraud_flags": 0
                },
                "policy_id": "POL-AUTO-456789",
                "policy_start_date": "2025-06-01T00:00:00Z",
                "policy_premium": "1200.00",
                "has_police_report": True,
                "has_witness_statements": False,
                "has_medical_records": False,
                "has_photos": True,
                "metadata": {
                    "channel": "mobile_app",
                    "adjuster_id": "ADJ-123"
                }
            }
        }
    )


class FraudIndicator(BaseModel):
    """Individual fraud risk indicator."""
    
    indicator_name: str = Field(
        ...,
        description="Name of the fraud indicator"
    )
    indicator_type: str = Field(
        ...,
        description="Category of indicator (behavioral, temporal, financial, etc.)"
    )
    risk_contribution: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Contribution to overall fraud risk (0-1)"
    )
    description: str = Field(
        ...,
        description="Human-readable explanation of this indicator"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Supporting evidence or data points"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "indicator_name": "high_claim_frequency",
                "indicator_type": "behavioral",
                "risk_contribution": 0.35,
                "description": "Claimant has filed 3 claims in the last 6 months, significantly above average",
                "evidence": [
                    "3 claims in 6 months vs. industry avg of 0.5",
                    "Claims increasing in severity over time"
                ]
            }
        }
    )


class FraudOutput(BaseModel):
    """Output schema for fraud detection analysis.
    
    Standardized output following platform conventions.
    Matches the standard decision output format.
    """
    
    # Standard platform fields
    decision_id: str = Field(
        ...,
        description="Unique identifier for this fraud decision"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this decision was made"
    )
    
    # Fraud-specific results
    claim_id: str = Field(
        ...,
        description="Reference to input claim ID"
    )
    fraud_risk_level: FraudRiskLevel = Field(
        ...,
        description="Overall fraud risk classification"
    )
    fraud_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Fraud probability score (0=no fraud, 1=definite fraud)"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the fraud assessment (0-1)"
    )
    
    # Detailed analysis
    fraud_indicators: List[FraudIndicator] = Field(
        default_factory=list,
        description="List of fraud indicators detected"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="Summary of key risk factors"
    )
    
    # Recommendations
    recommended_action: str = Field(
        ...,
        description="Recommended next action (approve, investigate, deny, escalate)"
    )
    investigation_priority: str = Field(
        ...,
        description="Investigation priority level (low, medium, high, urgent)"
    )
    suggested_steps: List[str] = Field(
        default_factory=list,
        description="Suggested investigation or verification steps"
    )
    
    # Human-in-the-loop
    requires_human_review: bool = Field(
        ...,
        description="Whether human review is required before action"
    )
    review_reason: Optional[str] = Field(
        default=None,
        description="Reason why human review is required"
    )
    
    # Audit trail
    model_version: str = Field(
        ...,
        description="Version of fraud detection model used"
    )
    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Processing time in milliseconds"
    )
    
    # Additional context
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata or context"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "decision_id": "FRAUD-DEC-2026-001234",
                "timestamp": "2026-01-15T10:31:23Z",
                "claim_id": "CLM-2026-001234",
                "fraud_risk_level": "medium",
                "fraud_score": 0.62,
                "confidence": 0.85,
                "fraud_indicators": [
                    {
                        "indicator_name": "high_claim_frequency",
                        "indicator_type": "behavioral",
                        "risk_contribution": 0.35,
                        "description": "Multiple claims in short timeframe",
                        "evidence": ["3 claims in 6 months"]
                    }
                ],
                "risk_factors": [
                    "High claim frequency",
                    "Claim filed shortly after policy inception",
                    "Missing witness statements"
                ],
                "recommended_action": "investigate",
                "investigation_priority": "medium",
                "suggested_steps": [
                    "Verify incident location with traffic cameras",
                    "Contact police department for report details",
                    "Interview claimant about previous claims"
                ],
                "requires_human_review": True,
                "review_reason": "Fraud score above 0.6 threshold requires senior adjuster review",
                "model_version": "fraud-detector-v2.1.0",
                "processing_time_ms": 245.3,
                "metadata": {
                    "rules_triggered": ["R-FREQ-001", "R-TIME-003"],
                    "external_data_sources": ["police_db", "claims_history"]
                }
            }
        }
    )
