"""Mandatory Explainability for All Decisions.

Every decision must include structured explainability.
Explainability is NOT optional - it's required for audit and compliance.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class DecisionFactor(BaseModel):
    """A single factor that influenced the decision.
    
    Attributes:
        name: Human-readable factor name
        value: The value of this factor
        weight: Importance weight (0.0 to 1.0)
        impact: How this factor influenced the decision (positive/negative/neutral)
        description: Human-readable explanation
    """
    
    name: str = Field(..., description="Factor name")
    value: Any = Field(..., description="Factor value")
    weight: float = Field(
        ..., ge=0.0, le=1.0, description="Importance weight (0.0 to 1.0)"
    )
    impact: str = Field(
        ..., description="Impact direction: positive, negative, or neutral"
    )
    description: str = Field(
        ..., description="Human-readable explanation of this factor"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "claim_amount",
                "value": 75000.0,
                "weight": 0.8,
                "impact": "negative",
                "description": "High claim amount increases fraud risk"
            }
        }


class ScoredSignal(BaseModel):
    """A scored signal that contributed to the decision.
    
    Attributes:
        signal_name: Name of the signal
        score: Numeric score for this signal
        threshold: Threshold for this signal (if applicable)
        triggered: Whether this signal triggered an alert
        evidence: Supporting evidence for this signal
    """
    
    signal_name: str = Field(..., description="Signal name")
    score: float = Field(..., description="Numeric score")
    threshold: Optional[float] = Field(
        None, description="Threshold value (if applicable)"
    )
    triggered: bool = Field(
        ..., description="Whether this signal triggered an alert"
    )
    evidence: str = Field(
        ..., description="Supporting evidence for this signal"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "signal_name": "multiple_claims_short_period",
                "score": 0.85,
                "threshold": 0.7,
                "triggered": True,
                "evidence": "3 claims filed within 30 days"
            }
        }


class Evidence(BaseModel):
    """Structured evidence supporting the decision.
    
    Attributes:
        category: Evidence category (e.g., 'historical', 'behavioral', 'financial')
        items: List of evidence items
        confidence: Confidence in this evidence (0.0 to 1.0)
        source: Source of the evidence
    """
    
    category: str = Field(..., description="Evidence category")
    items: List[str] = Field(
        ..., description="List of evidence items"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in this evidence"
    )
    source: str = Field(
        ..., description="Source of the evidence"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "historical",
                "items": [
                    "No prior claims in 5 years",
                    "Policy in good standing",
                    "Timely premium payments"
                ],
                "confidence": 0.95,
                "source": "policy_database"
            }
        }


class Explainability(BaseModel):
    """Mandatory explainability payload for every decision.
    
    This is NOT optional. Every decision must include:
    - Human-readable summary
    - Key decision factors with weights
    - Scored signals that triggered
    - Structured evidence (not free text)
    
    Attributes:
        summary: Human-readable summary of the decision
        key_factors: List of key factors that influenced the decision
        scored_signals: List of scored signals that contributed
        evidence: Structured evidence supporting the decision
        confidence_score: Overall confidence in the decision (0.0 to 1.0)
        model_version: Version of the model/logic used
        explanation_metadata: Additional metadata for audit trail
    """
    
    summary: str = Field(
        ...,
        min_length=10,
        description="Human-readable summary of the decision (minimum 10 characters)"
    )
    key_factors: List[DecisionFactor] = Field(
        ...,
        min_length=1,
        description="Key factors that influenced the decision (at least 1 required)"
    )
    scored_signals: List[ScoredSignal] = Field(
        default_factory=list,
        description="Scored signals that contributed to the decision"
    )
    evidence: List[Evidence] = Field(
        default_factory=list,
        description="Structured evidence supporting the decision"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall confidence in the decision (0.0 to 1.0)"
    )
    model_version: str = Field(
        ..., description="Version of the model/logic used"
    )
    explanation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for audit trail"
    )
    
    def get_top_factors(self, n: int = 3) -> List[DecisionFactor]:
        """Get the top N factors by weight.
        
        Args:
            n: Number of top factors to return
        
        Returns:
            List of top N factors sorted by weight (descending).
        """
        return sorted(self.key_factors, key=lambda f: f.weight, reverse=True)[:n]
    
    def get_triggered_signals(self) -> List[ScoredSignal]:
        """Get all signals that triggered alerts.
        
        Returns:
            List of signals where triggered=True.
        """
        return [signal for signal in self.scored_signals if signal.triggered]
    
    def get_evidence_by_category(self, category: str) -> List[Evidence]:
        """Get evidence filtered by category.
        
        Args:
            category: Evidence category to filter by
        
        Returns:
            List of evidence matching the category.
        """
        return [e for e in self.evidence if e.category == category]
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if this is a high-confidence decision.
        
        Args:
            threshold: Confidence threshold (default 0.8)
        
        Returns:
            True if confidence_score >= threshold.
        """
        return self.confidence_score >= threshold
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "High-value claim with multiple fraud indicators requires investigation",
                "key_factors": [
                    {
                        "name": "claim_amount",
                        "value": 75000.0,
                        "weight": 0.8,
                        "impact": "negative",
                        "description": "Claim amount significantly above average"
                    },
                    {
                        "name": "claim_frequency",
                        "value": 3,
                        "weight": 0.6,
                        "impact": "negative",
                        "description": "Multiple claims in short period"
                    }
                ],
                "scored_signals": [
                    {
                        "signal_name": "high_value_claim",
                        "score": 0.9,
                        "threshold": 0.7,
                        "triggered": True,
                        "evidence": "Claim amount in top 5% of all claims"
                    }
                ],
                "evidence": [
                    {
                        "category": "financial",
                        "items": [
                            "Claim amount: $75,000",
                            "Policy limit: $100,000",
                            "Deductible: $1,000"
                        ],
                        "confidence": 1.0,
                        "source": "policy_system"
                    }
                ],
                "confidence_score": 0.85,
                "model_version": "fraud_detection_v1.2.0",
                "explanation_metadata": {
                    "total_factors_evaluated": 12,
                    "signals_triggered": 3,
                    "processing_time_ms": 145
                }
            }
        }
