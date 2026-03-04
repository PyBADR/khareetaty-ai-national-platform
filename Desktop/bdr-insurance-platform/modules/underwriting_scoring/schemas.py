"""Underwriting Scoring Module - Input/Output Schemas.

Standardized Pydantic schemas for insurance underwriting risk assessment.
Follows platform-wide schema conventions defined in modules/MODULE_TEMPLATE.md
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class InsuranceProduct(str, Enum):
    """Insurance product types."""
    AUTO = "auto"
    HOME = "home"
    LIFE = "life"
    HEALTH = "health"
    COMMERCIAL = "commercial"
    UMBRELLA = "umbrella"
    WORKERS_COMP = "workers_comp"


class RiskTier(str, Enum):
    """Risk tier classifications."""
    PREFERRED = "preferred"
    STANDARD = "standard"
    SUBSTANDARD = "substandard"
    DECLINED = "declined"


class UnderwritingDecision(str, Enum):
    """Underwriting decision outcomes."""
    APPROVE = "approve"
    APPROVE_WITH_CONDITIONS = "approve_with_conditions"
    REFER = "refer"
    DECLINE = "decline"


class ApplicantDemographics(BaseModel):
    """Applicant demographic information."""
    
    age: int = Field(
        ...,
        ge=16,
        le=120,
        description="Applicant age in years"
    )
    gender: Optional[str] = Field(
        default=None,
        description="Gender (if permitted by regulation)"
    )
    marital_status: Optional[str] = Field(
        default=None,
        description="Marital status"
    )
    occupation: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Occupation or profession"
    )
    years_at_occupation: int = Field(
        ...,
        ge=0,
        le=100,
        description="Years in current occupation"
    )
    education_level: Optional[str] = Field(
        default=None,
        description="Highest education level"
    )
    zip_code: str = Field(
        ...,
        min_length=5,
        max_length=10,
        description="Residential zip/postal code"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 35,
                "gender": "M",
                "marital_status": "married",
                "occupation": "Software Engineer",
                "years_at_occupation": 8,
                "education_level": "bachelors",
                "zip_code": "98101"
            }
        }
    )


class CreditHistory(BaseModel):
    """Credit and financial history information."""
    
    credit_score: Optional[int] = Field(
        default=None,
        ge=300,
        le=850,
        description="Credit score (FICO or equivalent)"
    )
    credit_tier: Optional[str] = Field(
        default=None,
        description="Credit tier classification (excellent, good, fair, poor)"
    )
    bankruptcies: int = Field(
        default=0,
        ge=0,
        description="Number of bankruptcies in last 7 years"
    )
    foreclosures: int = Field(
        default=0,
        ge=0,
        description="Number of foreclosures in last 7 years"
    )
    payment_history_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Payment history score (0=poor, 1=excellent)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "credit_score": 720,
                "credit_tier": "good",
                "bankruptcies": 0,
                "foreclosures": 0,
                "payment_history_score": 0.85
            }
        }
    )


class ClaimsHistory(BaseModel):
    """Insurance claims history."""
    
    total_claims_5_years: int = Field(
        ...,
        ge=0,
        description="Total claims in last 5 years"
    )
    at_fault_claims: int = Field(
        default=0,
        ge=0,
        description="Number of at-fault claims"
    )
    total_claims_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Total amount claimed in last 5 years"
    )
    largest_claim_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Largest single claim amount"
    )
    years_since_last_claim: Optional[float] = Field(
        default=None,
        ge=0,
        description="Years since last claim (null if no claims)"
    )
    claim_frequency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Claim frequency score (0=no claims, 1=very high frequency)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_claims_5_years": 1,
                "at_fault_claims": 0,
                "total_claims_amount": "3500.00",
                "largest_claim_amount": "3500.00",
                "years_since_last_claim": 2.5,
                "claim_frequency_score": 0.15
            }
        }
    )


class CoverageRequest(BaseModel):
    """Requested coverage details."""
    
    coverage_amount: Decimal = Field(
        ...,
        ge=0,
        description="Requested coverage/sum insured amount"
    )
    deductible: Decimal = Field(
        ...,
        ge=0,
        description="Requested deductible amount"
    )
    coverage_term_months: int = Field(
        ...,
        ge=1,
        le=1200,
        description="Coverage term in months"
    )
    additional_coverages: List[str] = Field(
        default_factory=list,
        description="List of additional coverage options requested"
    )
    riders: List[str] = Field(
        default_factory=list,
        description="List of policy riders requested"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "coverage_amount": "500000.00",
                "deductible": "1000.00",
                "coverage_term_months": 12,
                "additional_coverages": ["collision", "comprehensive"],
                "riders": ["roadside_assistance"]
            }
        }
    )


class RiskFactors(BaseModel):
    """Product-specific risk factors."""
    
    # Auto-specific
    driving_record_points: Optional[int] = Field(
        default=None,
        ge=0,
        description="Driving record points (auto insurance)"
    )
    annual_mileage: Optional[int] = Field(
        default=None,
        ge=0,
        description="Annual mileage (auto insurance)"
    )
    vehicle_age_years: Optional[int] = Field(
        default=None,
        ge=0,
        description="Vehicle age in years (auto insurance)"
    )
    
    # Home-specific
    home_age_years: Optional[int] = Field(
        default=None,
        ge=0,
        description="Home age in years (home insurance)"
    )
    construction_type: Optional[str] = Field(
        default=None,
        description="Construction type (home insurance)"
    )
    security_features: Optional[List[str]] = Field(
        default=None,
        description="Security features (home insurance)"
    )
    
    # Life/Health-specific
    smoker: Optional[bool] = Field(
        default=None,
        description="Smoker status (life/health insurance)"
    )
    bmi: Optional[float] = Field(
        default=None,
        ge=10.0,
        le=100.0,
        description="Body Mass Index (life/health insurance)"
    )
    pre_existing_conditions: Optional[List[str]] = Field(
        default=None,
        description="Pre-existing medical conditions (health insurance)"
    )
    
    # General
    hazard_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="General hazard/risk score (0=low, 1=high)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "driving_record_points": 0,
                "annual_mileage": 12000,
                "vehicle_age_years": 3,
                "hazard_score": 0.25
            }
        }
    )


class UnderwritingInput(BaseModel):
    """Input schema for underwriting risk assessment.
    
    Standardized input following platform conventions.
    All underwriting requests must conform to this schema.
    """
    
    # Application identification
    application_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique application identifier"
    )
    product_type: InsuranceProduct = Field(
        ...,
        description="Type of insurance product"
    )
    application_date: datetime = Field(
        ...,
        description="Date and time application was submitted"
    )
    
    # Applicant information
    applicant_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique applicant identifier"
    )
    demographics: ApplicantDemographics = Field(
        ...,
        description="Applicant demographic information"
    )
    
    # Financial and credit
    credit_history: CreditHistory = Field(
        ...,
        description="Credit and financial history"
    )
    annual_income: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Annual income (if required for product)"
    )
    
    # Insurance history
    claims_history: ClaimsHistory = Field(
        ...,
        description="Insurance claims history"
    )
    years_continuously_insured: float = Field(
        ...,
        ge=0,
        description="Years continuously insured (0 if new to insurance)"
    )
    prior_insurance_lapse: bool = Field(
        default=False,
        description="Whether there was a lapse in prior insurance coverage"
    )
    
    # Coverage request
    coverage_request: CoverageRequest = Field(
        ...,
        description="Requested coverage details"
    )
    
    # Risk factors
    risk_factors: RiskFactors = Field(
        ...,
        description="Product-specific risk factors"
    )
    
    # External data
    third_party_reports: Dict[str, Any] = Field(
        default_factory=dict,
        description="Third-party reports (MVR, CLUE, MIB, etc.)"
    )
    
    # Underwriting guidelines
    apply_strict_guidelines: bool = Field(
        default=False,
        description="Whether to apply strict underwriting guidelines"
    )
    
    # Context
    distribution_channel: str = Field(
        ...,
        description="Distribution channel (agent, direct, broker, online)"
    )
    state_province: str = Field(
        ...,
        min_length=2,
        max_length=3,
        description="State or province code"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or metadata"
    )

    @field_validator('coverage_request')
    @classmethod
    def validate_coverage_reasonable(cls, v: CoverageRequest, info) -> CoverageRequest:
        """Validate coverage request is reasonable."""
        # Example: deductible shouldn't exceed coverage amount
        if v.deductible > v.coverage_amount:
            raise ValueError('Deductible cannot exceed coverage amount')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "application_id": "UW-APP-2026-001234",
                "product_type": "auto",
                "application_date": "2026-01-20T14:30:00Z",
                "applicant_id": "APPL-789456",
                "demographics": {
                    "age": 35,
                    "gender": "M",
                    "marital_status": "married",
                    "occupation": "Software Engineer",
                    "years_at_occupation": 8,
                    "education_level": "bachelors",
                    "zip_code": "98101"
                },
                "credit_history": {
                    "credit_score": 720,
                    "credit_tier": "good",
                    "bankruptcies": 0,
                    "foreclosures": 0,
                    "payment_history_score": 0.85
                },
                "annual_income": "95000.00",
                "claims_history": {
                    "total_claims_5_years": 1,
                    "at_fault_claims": 0,
                    "total_claims_amount": "3500.00",
                    "largest_claim_amount": "3500.00",
                    "years_since_last_claim": 2.5,
                    "claim_frequency_score": 0.15
                },
                "years_continuously_insured": 10.0,
                "prior_insurance_lapse": False,
                "coverage_request": {
                    "coverage_amount": "500000.00",
                    "deductible": "1000.00",
                    "coverage_term_months": 12,
                    "additional_coverages": ["collision", "comprehensive"],
                    "riders": ["roadside_assistance"]
                },
                "risk_factors": {
                    "driving_record_points": 0,
                    "annual_mileage": 12000,
                    "vehicle_age_years": 3,
                    "hazard_score": 0.25
                },
                "third_party_reports": {
                    "mvr_score": 85,
                    "clue_report_available": True
                },
                "apply_strict_guidelines": False,
                "distribution_channel": "online",
                "state_province": "WA",
                "metadata": {
                    "referral_source": "google_ads",
                    "quote_id": "QT-2026-001234"
                }
            }
        }
    )


class RiskScore(BaseModel):
    """Individual risk scoring component."""
    
    score_name: str = Field(
        ...,
        description="Name of the risk score"
    )
    score_value: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score value (0=lowest risk, 1=highest risk)"
    )
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weight in overall risk calculation"
    )
    description: str = Field(
        ...,
        description="Description of what this score measures"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "score_name": "claims_frequency",
                "score_value": 0.15,
                "weight": 0.30,
                "description": "Risk based on historical claims frequency"
            }
        }
    )


class PricingRecommendation(BaseModel):
    """Pricing recommendation details."""
    
    base_premium: Decimal = Field(
        ...,
        ge=0,
        description="Base premium before adjustments"
    )
    risk_adjustment_factor: float = Field(
        ...,
        ge=0.0,
        description="Risk adjustment multiplier"
    )
    recommended_premium: Decimal = Field(
        ...,
        ge=0,
        description="Final recommended premium"
    )
    premium_range_min: Decimal = Field(
        ...,
        ge=0,
        description="Minimum acceptable premium"
    )
    premium_range_max: Decimal = Field(
        ...,
        ge=0,
        description="Maximum acceptable premium"
    )
    discount_eligibility: List[str] = Field(
        default_factory=list,
        description="List of discounts applicant is eligible for"
    )
    surcharges: List[str] = Field(
        default_factory=list,
        description="List of surcharges that apply"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "base_premium": "1200.00",
                "risk_adjustment_factor": 0.95,
                "recommended_premium": "1140.00",
                "premium_range_min": "1080.00",
                "premium_range_max": "1260.00",
                "discount_eligibility": ["good_driver", "multi_policy"],
                "surcharges": []
            }
        }
    )


class UnderwritingCondition(BaseModel):
    """Condition or requirement for approval."""
    
    condition_type: str = Field(
        ...,
        description="Type of condition (documentation, inspection, exclusion, etc.)"
    )
    description: str = Field(
        ...,
        description="Description of the condition"
    )
    required_by_date: Optional[date] = Field(
        default=None,
        description="Date by which condition must be satisfied"
    )
    is_mandatory: bool = Field(
        default=True,
        description="Whether this condition is mandatory for approval"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "condition_type": "documentation",
                "description": "Provide proof of prior insurance coverage",
                "required_by_date": "2026-02-01",
                "is_mandatory": True
            }
        }
    )


class UnderwritingOutput(BaseModel):
    """Output schema for underwriting risk assessment.
    
    Standardized output following platform conventions.
    Matches the standard decision output format.
    """
    
    # Standard platform fields
    decision_id: str = Field(
        ...,
        description="Unique identifier for this underwriting decision"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this decision was made"
    )
    
    # Reference data
    application_id: str = Field(
        ...,
        description="Reference to input application ID"
    )
    applicant_id: str = Field(
        ...,
        description="Reference to applicant ID"
    )
    
    # Underwriting decision
    decision: UnderwritingDecision = Field(
        ...,
        description="Underwriting decision outcome"
    )
    risk_tier: RiskTier = Field(
        ...,
        description="Risk tier classification"
    )
    
    # Risk assessment
    overall_risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall risk score (0=lowest risk, 1=highest risk)"
    )
    risk_scores: List[RiskScore] = Field(
        default_factory=list,
        description="Breakdown of individual risk scores"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the underwriting assessment (0-1)"
    )
    
    # Pricing
    pricing_recommendation: Optional[PricingRecommendation] = Field(
        default=None,
        description="Pricing recommendation (if decision is approve or approve_with_conditions)"
    )
    
    # Conditions and requirements
    conditions: List[UnderwritingCondition] = Field(
        default_factory=list,
        description="Conditions or requirements for approval"
    )
    
    # Decline reasons (if applicable)
    decline_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for decline (if decision is decline)"
    )
    
    # Referral reasons (if applicable)
    referral_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons for referral to underwriter (if decision is refer)"
    )
    
    # Key factors
    positive_factors: List[str] = Field(
        default_factory=list,
        description="Positive factors that reduced risk"
    )
    negative_factors: List[str] = Field(
        default_factory=list,
        description="Negative factors that increased risk"
    )
    
    # Recommendations
    underwriter_notes: Optional[str] = Field(
        default=None,
        description="Notes for underwriter review (if referral)"
    )
    suggested_actions: List[str] = Field(
        default_factory=list,
        description="Suggested next actions"
    )
    
    # Human-in-the-loop
    requires_underwriter_review: bool = Field(
        ...,
        description="Whether underwriter review is required"
    )
    review_reason: Optional[str] = Field(
        default=None,
        description="Reason why underwriter review is required"
    )
    assigned_underwriter: Optional[str] = Field(
        default=None,
        description="Underwriter assigned for review (if applicable)"
    )
    
    # Compliance
    regulatory_flags: List[str] = Field(
        default_factory=list,
        description="Any regulatory compliance flags or notes"
    )
    fair_lending_review: bool = Field(
        default=False,
        description="Whether fair lending review was triggered"
    )
    
    # Audit trail
    model_version: str = Field(
        ...,
        description="Version of underwriting model used"
    )
    guidelines_version: str = Field(
        ...,
        description="Version of underwriting guidelines applied"
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
                "decision_id": "UW-DEC-2026-001234",
                "timestamp": "2026-01-20T14:31:45Z",
                "application_id": "UW-APP-2026-001234",
                "applicant_id": "APPL-789456",
                "decision": "approve",
                "risk_tier": "standard",
                "overall_risk_score": 0.35,
                "risk_scores": [
                    {
                        "score_name": "claims_frequency",
                        "score_value": 0.15,
                        "weight": 0.30,
                        "description": "Risk based on historical claims frequency"
                    },
                    {
                        "score_name": "credit_risk",
                        "score_value": 0.25,
                        "weight": 0.25,
                        "description": "Risk based on credit history"
                    }
                ],
                "confidence": 0.92,
                "pricing_recommendation": {
                    "base_premium": "1200.00",
                    "risk_adjustment_factor": 0.95,
                    "recommended_premium": "1140.00",
                    "premium_range_min": "1080.00",
                    "premium_range_max": "1260.00",
                    "discount_eligibility": ["good_driver", "multi_policy"],
                    "surcharges": []
                },
                "conditions": [],
                "decline_reasons": [],
                "referral_reasons": [],
                "positive_factors": [
                    "Good credit score (720)",
                    "10 years continuous insurance",
                    "Clean driving record"
                ],
                "negative_factors": [
                    "One claim in last 5 years"
                ],
                "suggested_actions": [
                    "Generate quote with recommended premium",
                    "Offer multi-policy discount"
                ],
                "requires_underwriter_review": False,
                "regulatory_flags": [],
                "fair_lending_review": False,
                "model_version": "underwriting-engine-v3.2.1",
                "guidelines_version": "2026_Q1_WA",
                "processing_time_ms": 312.5,
                "metadata": {
                    "rules_applied": ["UW-AUTO-001", "UW-CREDIT-002"],
                    "data_sources": ["mvr", "clue", "credit_bureau"]
                }
            }
        }
    )
