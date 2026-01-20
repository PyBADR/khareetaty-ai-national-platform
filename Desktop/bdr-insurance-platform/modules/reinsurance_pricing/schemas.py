"Reinsurance Pricing Module - Input/Output Schemas.

Standardized Pydantic schemas for reinsurance treaty pricing and risk transfer analysis.
Follows platform-wide schema conventions defined in modules/MODULE_TEMPLATE.md
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class TreatyType(str, Enum):
    """Reinsurance treaty types."""
    QUOTA_SHARE = "quota_share"
    SURPLUS = "surplus"
    EXCESS_OF_LOSS = "excess_of_loss"
    STOP_LOSS = "stop_loss"
    CATASTROPHE = "catastrophe"
    FACULTATIVE = "facultative"


class PricingBasis(str, Enum):
    """Pricing calculation basis."""
    BURNING_COST = "burning_cost"
    EXPOSURE_RATING = "exposure_rating"
    EXPERIENCE_RATING = "experience_rating"
    CATASTROPHE_MODEL = "catastrophe_model"
    HYBRID = "hybrid"


class AttachmentBasis(str, Enum):
    """Attachment point basis."""
    PER_OCCURRENCE = "per_occurrence"
    PER_RISK = "per_risk"
    AGGREGATE = "aggregate"
    ANNUAL_AGGREGATE = "annual_aggregate"


class LossData(BaseModel):
    """Historical loss data point."""
    
    accident_year: int = Field(
        ...,
        ge=1900,
        le=2100,
        description="Accident year"
    )
    gross_losses: Decimal = Field(
        ...,
        ge=0,
        description="Gross losses for the year"
    )
    ceded_losses: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Losses ceded to reinsurance"
    )
    net_losses: Decimal = Field(
        ...,
        ge=0,
        description="Net losses retained"
    )
    earned_premium: Decimal = Field(
        ...,
        ge=0,
        description="Earned premium for the year"
    )
    loss_ratio: float = Field(
        ...,
        ge=0.0,
        description="Loss ratio (losses / premium)"
    )
    development_factor: float = Field(
        default=1.0,
        ge=0.0,
        description="Loss development factor to ultimate"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "accident_year": 2023,
                "gross_losses": "8500000.00",
                "ceded_losses": "2000000.00",
                "net_losses": "6500000.00",
                "earned_premium": "12000000.00",
                "loss_ratio": 0.708,
                "development_factor": 1.15
            }
        }
    )


class ExposureData(BaseModel):
    """Exposure data for rating."""
    
    total_insured_value: Decimal = Field(
        ...,
        ge=0,
        description="Total insured value (TIV)"
    )
    number_of_risks: int = Field(
        ...,
        ge=0,
        description="Number of individual risks"
    )
    average_risk_size: Decimal = Field(
        ...,
        ge=0,
        description="Average size per risk"
    )
    maximum_risk_size: Decimal = Field(
        ...,
        ge=0,
        description="Maximum single risk size"
    )
    geographic_concentration: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Geographic distribution (region: TIV)"
    )
    industry_concentration: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Industry distribution (sector: TIV)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_insured_value": "500000000.00",
                "number_of_risks": 1250,
                "average_risk_size": "400000.00",
                "maximum_risk_size": "5000000.00",
                "geographic_concentration": {
                    "california": "150000000.00",
                    "texas": "100000000.00",
                    "florida": "80000000.00"
                },
                "industry_concentration": {
                    "manufacturing": "200000000.00",
                    "retail": "150000000.00"
                }
            }
        }
    )


class TreatyStructure(BaseModel):
    """Reinsurance treaty structure parameters."""
    
    treaty_type: TreatyType = Field(
        ...,
        description="Type of reinsurance treaty"
    )
    
    # Quota Share / Surplus specific
    cession_percentage: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Cession percentage (for quota share)"
    )
    retention_limit: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Retention limit per risk (for surplus)"
    )
    number_of_lines: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of lines (for surplus)"
    )
    
    # Excess of Loss specific
    attachment_point: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Attachment point / retention"
    )
    limit: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Reinsurance limit"
    )
    attachment_basis: Optional[AttachmentBasis] = Field(
        default=None,
        description="Basis for attachment (per occurrence, aggregate, etc.)"
    )
    
    # Reinstatements
    number_of_reinstatements: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Number of reinstatements allowed"
    )
    reinstatement_premiums: List[float] = Field(
        default_factory=list,
        description="Reinstatement premium percentages (e.g., [100, 100] for 2 at 100%)"
    )
    
    # Commission
    ceding_commission: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ceding commission percentage"
    )
    profit_commission: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Profit commission percentage (if applicable)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "treaty_type": "excess_of_loss",
                "attachment_point": "1000000.00",
                "limit": "4000000.00",
                "attachment_basis": "per_occurrence",
                "number_of_reinstatements": 2,
                "reinstatement_premiums": [100.0, 100.0],
                "ceding_commission": 0.25
            }
        }
    )


class CatastropheModel(BaseModel):
    """Catastrophe modeling parameters."""
    
    model_vendor: str = Field(
        ...,
        description="Catastrophe model vendor (RMS, AIR, CoreLogic, etc.)"
    )
    model_version: str = Field(
        ...,
        description="Model version"
    )
    perils_modeled: List[str] = Field(
        ...,
        description="List of perils modeled (earthquake, hurricane, flood, etc.)"
    )
    return_periods: List[int] = Field(
        ...,
        description="Return periods analyzed (e.g., [100, 250, 500, 1000])"
    )
    average_annual_loss: Decimal = Field(
        ...,
        ge=0,
        description="Average Annual Loss (AAL) from model"
    )
    probable_maximum_loss: Dict[int, Decimal] = Field(
        ...,
        description="PML by return period (e.g., {250: 5000000})"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "model_vendor": "RMS",
                "model_version": "v21.0",
                "perils_modeled": ["earthquake", "hurricane", "wildfire"],
                "return_periods": [100, 250, 500, 1000],
                "average_annual_loss": "850000.00",
                "probable_maximum_loss": {
                    "100": "3500000.00",
                    "250": "7500000.00",
                    "500": "12000000.00",
                    "1000": "18000000.00"
                }
            }
        }
    )


class ReinsuranceInput(BaseModel):
    """Input schema for reinsurance pricing analysis.
    
    Standardized input following platform conventions.
    All reinsurance pricing requests must conform to this schema.
    """
    
    # Treaty identification
    treaty_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique treaty identifier"
    )
    treaty_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Treaty name or description"
    )
    inception_date: date = Field(
        ...,
        description="Treaty inception date"
    )
    expiration_date: date = Field(
        ...,
        description="Treaty expiration date"
    )
    
    # Cedent information
    cedent_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Cedent (ceding company) identifier"
    )
    cedent_name: str = Field(
        ...,
        description="Cedent company name"
    )
    
    # Treaty structure
    treaty_structure: TreatyStructure = Field(
        ...,
        description="Reinsurance treaty structure"
    )
    
    # Subject premium
    subject_premium: Decimal = Field(
        ...,
        ge=0,
        description="Subject premium (gross premium subject to treaty)"
    )
    
    # Historical loss data
    historical_losses: List[LossData] = Field(
        ...,
        min_length=1,
        description="Historical loss data (minimum 1 year, typically 5-10 years)"
    )
    
    # Exposure data
    exposure_data: ExposureData = Field(
        ...,
        description="Current exposure data"
    )
    
    # Catastrophe modeling (if applicable)
    catastrophe_model: Optional[CatastropheModel] = Field(
        default=None,
        description="Catastrophe model results (for cat XOL treaties)"
    )
    
    # Pricing parameters
    pricing_basis: PricingBasis = Field(
        ...,
        description="Primary pricing methodology to use"
    )
    target_loss_ratio: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Target loss ratio for pricing (if specified)"
    )
    expense_ratio: float = Field(
        default=0.05,
        ge=0.0,
        le=0.5,
        description="Expense ratio (reinsurer's expenses)"
    )
    profit_margin: float = Field(
        default=0.10,
        ge=0.0,
        le=0.5,
        description="Target profit margin"
    )
    
    # Risk adjustments
    trend_factor: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Loss trend factor (1.0 = no trend)"
    )
    large_loss_loading: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Additional loading for large loss potential"
    )
    
    # Market conditions
    market_conditions: str = Field(
        default="balanced",
        description="Market conditions (soft, balanced, hard)"
    )
    competitive_quotes: List[Decimal] = Field(
        default_factory=list,
        description="Competitive quotes from other reinsurers (if available)"
    )
    
    # Context
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)"
    )
    business_line: str = Field(
        ...,
        description="Line of business (property, casualty, specialty, etc.)"
    )
    geographic_scope: List[str] = Field(
        ...,
        description="Geographic scope (countries/regions covered)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or metadata"
    )

    @field_validator('expiration_date')
    @classmethod
    def expiration_after_inception(cls, v: date, info) -> date:
        """Validate expiration is after inception."""
        if 'inception_date' in info.data and v <= info.data['inception_date']:
            raise ValueError('Expiration date must be after inception date')
        return v

    @field_validator('historical_losses')
    @classmethod
    def validate_loss_data(cls, v: List[LossData]) -> List[LossData]:
        """Validate historical loss data is reasonable."""
        if len(v) < 1:
            raise ValueError('At least 1 year of historical loss data required')
        # Check years are unique
        years = [loss.accident_year for loss in v]
        if len(years) != len(set(years)):
            raise ValueError('Duplicate accident years in historical loss data')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "treaty_id": "REINS-2026-XOL-001",
                "treaty_name": "Property Catastrophe XOL 2026",
                "inception_date": "2026-01-01",
                "expiration_date": "2026-12-31",
                "cedent_id": "CED-12345",
                "cedent_name": "ABC Insurance Company",
                "treaty_structure": {
                    "treaty_type": "excess_of_loss",
                    "attachment_point": "5000000.00",
                    "limit": "20000000.00",
                    "attachment_basis": "per_occurrence",
                    "number_of_reinstatements": 1,
                    "reinstatement_premiums": [100.0],
                    "ceding_commission": 0.0
                },
                "subject_premium": "25000000.00",
                "historical_losses": [
                    {
                        "accident_year": 2023,
                        "gross_losses": "8500000.00",
                        "ceded_losses": "2000000.00",
                        "net_losses": "6500000.00",
                        "earned_premium": "22000000.00",
                        "loss_ratio": 0.386,
                        "development_factor": 1.05
                    }
                ],
                "exposure_data": {
                    "total_insured_value": "5000000000.00",
                    "number_of_risks": 15000,
                    "average_risk_size": "333333.00",
                    "maximum_risk_size": "10000000.00",
                    "geographic_concentration": {
                        "california": "1500000000.00",
                        "texas": "1000000000.00"
                    },
                    "industry_concentration": {
                        "residential": "3000000000.00",
                        "commercial": "2000000000.00"
                    }
                },
                "catastrophe_model": {
                    "model_vendor": "RMS",
                    "model_version": "v21.0",
                    "perils_modeled": ["earthquake", "hurricane"],
                    "return_periods": [100, 250, 500],
                    "average_annual_loss": "1200000.00",
                    "probable_maximum_loss": {
                        "100": "8000000.00",
                        "250": "15000000.00",
                        "500": "25000000.00"
                    }
                },
                "pricing_basis": "catastrophe_model",
                "target_loss_ratio": 0.65,
                "expense_ratio": 0.05,
                "profit_margin": 0.10,
                "trend_factor": 1.03,
                "large_loss_loading": 0.05,
                "market_conditions": "balanced",
                "competitive_quotes": ["2500000.00", "2750000.00"],
                "currency": "USD",
                "business_line": "property",
                "geographic_scope": ["USA"],
                "metadata": {
                    "broker": "Aon",
                    "renewal": True
                }
            }
        }
    )


class PricingComponent(BaseModel):
    """Individual pricing component breakdown."""
    
    component_name: str = Field(
        ...,
        description="Name of pricing component"
    )
    amount: Decimal = Field(
        ...,
        description="Component amount"
    )
    percentage_of_premium: float = Field(
        ...,
        ge=0.0,
        description="Percentage of total premium"
    )
    description: str = Field(
        ...,
        description="Description of this component"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_name": "expected_loss_cost",
                "amount": "1500000.00",
                "percentage_of_premium": 0.60,
                "description": "Expected loss cost based on cat model"
            }
        }
    )


class LayerAnalysis(BaseModel):
    """Analysis of specific treaty layer."""
    
    attachment_point: Decimal = Field(
        ...,
        ge=0,
        description="Layer attachment point"
    )
    limit: Decimal = Field(
        ...,
        ge=0,
        description="Layer limit"
    )
    expected_loss_cost: Decimal = Field(
        ...,
        ge=0,
        description="Expected loss cost for this layer"
    )
    loss_cost_rate: float = Field(
        ...,
        ge=0.0,
        description="Loss cost as rate on subject premium"
    )
    probability_of_attachment: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability layer will attach"
    )
    expected_frequency: float = Field(
        ...,
        ge=0.0,
        description="Expected number of losses penetrating layer"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "attachment_point": "5000000.00",
                "limit": "20000000.00",
                "expected_loss_cost": "1500000.00",
                "loss_cost_rate": 0.06,
                "probability_of_attachment": 0.15,
                "expected_frequency": 0.25
            }
        }
    )


class ReinsuranceOutput(BaseModel):
    """Output schema for reinsurance pricing analysis.
    
    Standardized output following platform conventions.
    Matches the standard decision output format.
    """
    
    # Standard platform fields
    decision_id: str = Field(
        ...,
        description="Unique identifier for this pricing decision"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this pricing was calculated"
    )
    
    # Reference data
    treaty_id: str = Field(
        ...,
        description="Reference to input treaty ID"
    )
    treaty_name: str = Field(
        ...,
        description="Treaty name"
    )
    
    # Pricing recommendation
    recommended_premium: Decimal = Field(
        ...,
        ge=0,
        description="Recommended reinsurance premium"
    )
    premium_rate: float = Field(
        ...,
        ge=0.0,
        description="Premium as rate on subject premium"
    )
    
    # Pricing range
    minimum_premium: Decimal = Field(
        ...,
        ge=0,
        description="Minimum acceptable premium"
    )
    maximum_premium: Decimal = Field(
        ...,
        ge=0,
        description="Maximum competitive premium"
    )
    technical_price: Decimal = Field(
        ...,
        ge=0,
        description="Technical price (before market adjustments)"
    )
    
    # Pricing components
    pricing_components: List[PricingComponent] = Field(
        default_factory=list,
        description="Breakdown of pricing components"
    )
    
    # Loss metrics
    expected_loss_cost: Decimal = Field(
        ...,
        ge=0,
        description="Expected loss cost"
    )
    expected_loss_ratio: float = Field(
        ...,
        ge=0.0,
        description="Expected loss ratio"
    )
    burning_cost: Decimal = Field(
        ...,
        ge=0,
        description="Historical burning cost"
    )
    
    # Layer analysis
    layer_analysis: Optional[LayerAnalysis] = Field(
        default=None,
        description="Detailed layer analysis (for XOL treaties)"
    )
    
    # Risk metrics
    coefficient_of_variation: float = Field(
        ...,
        ge=0.0,
        description="Coefficient of variation (volatility measure)"
    )
    tail_value_at_risk: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Tail VaR at 99% confidence level"
    )
    return_on_capital: float = Field(
        ...,
        description="Expected return on allocated capital"
    )
    
    # Pricing basis used
    primary_pricing_method: str = Field(
        ...,
        description="Primary pricing method used"
    )
    secondary_methods: List[str] = Field(
        default_factory=list,
        description="Secondary methods used for validation"
    )
    
    # Market positioning
    market_competitiveness: str = Field(
        ...,
        description="Market competitiveness assessment (competitive, market, aggressive)"
    )
    competitive_position: Optional[str] = Field(
        default=None,
        description="Position vs competitive quotes (if available)"
    )
    
    # Recommendations
    underwriting_recommendations: List[str] = Field(
        default_factory=list,
        description="Underwriting recommendations or conditions"
    )
    risk_mitigation_suggestions: List[str] = Field(
        default_factory=list,
        description="Suggested risk mitigation measures"
    )
    
    # Sensitivity analysis
    sensitivity_to_loss_ratio: Dict[str, Decimal] = Field(
        default_factory=dict,
        description="Premium sensitivity to loss ratio changes (e.g., {'+10%': 2750000})"
    )
    
    # Human-in-the-loop
    requires_pricing_committee: bool = Field(
        ...,
        description="Whether pricing committee review is required"
    )
    review_reason: Optional[str] = Field(
        default=None,
        description="Reason why committee review is required"
    )
    
    # Confidence and validation
    pricing_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in pricing recommendation (0-1)"
    )
    data_quality_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Quality score for input data (0-1)"
    )
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="Any validation warnings or data quality issues"
    )
    
    # Audit trail
    model_version: str = Field(
        ...,
        description="Version of pricing model used"
    )
    processing_time_ms: float = Field(
        ...,
        ge=0,
        description="Processing time in milliseconds"
    )
    
    # Additional context
    currency: str = Field(
        default="USD",
        description="Currency code"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata or context"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "decision_id": "REINS-PRICE-2026-001",
                "timestamp": "2026-01-20T16:45:00Z",
                "treaty_id": "REINS-2026-XOL-001",
                "treaty_name": "Property Catastrophe XOL 2026",
                "recommended_premium": "2500000.00",
                "premium_rate": 0.10,
                "minimum_premium": "2250000.00",
                "maximum_premium": "2750000.00",
                "technical_price": "2450000.00",
                "pricing_components": [
                    {
                        "component_name": "expected_loss_cost",
                        "amount": "1500000.00",
                        "percentage_of_premium": 0.60,
                        "description": "Expected loss cost from cat model"
                    },
                    {
                        "component_name": "expense_loading",
                        "amount": "125000.00",
                        "percentage_of_premium": 0.05,
                        "description": "Reinsurer expense loading"
                    },
                    {
                        "component_name": "profit_margin",
                        "amount": "250000.00",
                        "percentage_of_premium": 0.10,
                        "description": "Target profit margin"
                    },
                    {
                        "component_name": "risk_margin",
                        "amount": "625000.00",
                        "percentage_of_premium": 0.25,
                        "description": "Risk margin for volatility and uncertainty"
                    }
                ],
                "expected_loss_cost": "1500000.00",
                "expected_loss_ratio": 0.60,
                "burning_cost": "1350000.00",
                "layer_analysis": {
                    "attachment_point": "5000000.00",
                    "limit": "20000000.00",
                    "expected_loss_cost": "1500000.00",
                    "loss_cost_rate": 0.06,
                    "probability_of_attachment": 0.15,
                    "expected_frequency": 0.25
                },
                "coefficient_of_variation": 2.5,
                "tail_value_at_risk": "18000000.00",
                "return_on_capital": 0.12,
                "primary_pricing_method": "catastrophe_model",
                "secondary_methods": ["burning_cost", "exposure_rating"],
                "market_competitiveness": "competitive",
                "competitive_position": "Mid-market vs 2 quotes",
                "underwriting_recommendations": [
                    "Require annual exposure reporting",
                    "Include wildfire sub-limit of $10M"
                ],
                "risk_mitigation_suggestions": [
                    "Consider aggregate deductible",
                    "Exclude certain high-hazard zones"
                ],
                "sensitivity_to_loss_ratio": {
                    "+10%": "2750000.00",
                    "-10%": "2250000.00"
                },
                "requires_pricing_committee": True,
                "review_reason": "Premium exceeds $2M threshold requiring committee approval",
                "pricing_confidence": 0.85,
                "data_quality_score": 0.90,
                "validation_warnings": [
                    "Limited historical data (3 years)"
                ],
                "model_version": "reinsurance-pricer-v2.3.0",
                "processing_time_ms": 1250.5,
                "currency": "USD",
                "metadata": {
                    "cat_model_run_id": "RMS-2026-001",
                    "market_intel_source": "Guy_Carpenter_Q1_2026"
                }
            }
        }
    )
