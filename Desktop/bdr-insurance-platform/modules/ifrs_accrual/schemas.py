"""IFRS Accrual Module - Input/Output Schemas.

Standardized Pydantic schemas for IFRS 17 insurance contract accrual calculations.
Follows platform-wide schema conventions defined in modules/MODULE_TEMPLATE.md
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ContractType(str, Enum):
    """IFRS 17 contract classification types."""
    PAA = "paa"  # Premium Allocation Approach
    BBA = "bba"  # Building Block Approach (General Model)
    VFA = "vfa"  # Variable Fee Approach


class CoverageUnit(str, Enum):
    """Coverage measurement units."""
    SUM_INSURED = "sum_insured"
    PREMIUM = "premium"
    CLAIMS_EXPECTED = "claims_expected"
    TIME_BASED = "time_based"


class DiscountCurve(str, Enum):
    """Discount curve types for present value calculations."""
    RISK_FREE = "risk_free"
    SWAP_CURVE = "swap_curve"
    GOVERNMENT_BOND = "government_bond"
    CUSTOM = "custom"


class CashFlowPattern(BaseModel):
    """Expected cash flow pattern for contract."""
    
    period_months: int = Field(
        ...,
        ge=1,
        le=1200,  # Up to 100 years
        description="Period in months from contract inception"
    )
    expected_premium: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Expected premium inflow for this period"
    )
    expected_claims: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Expected claims outflow for this period"
    )
    expected_expenses: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Expected expenses for this period"
    )
    probability_weight: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Probability weight for this scenario (for stochastic modeling)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "period_months": 12,
                "expected_premium": "1200.00",
                "expected_claims": "800.00",
                "expected_expenses": "150.00",
                "probability_weight": 1.0
            }
        }
    )


class RiskAdjustment(BaseModel):
    """Risk adjustment parameters for non-financial risk."""
    
    confidence_level: float = Field(
        ...,
        ge=0.5,
        le=0.999,
        description="Confidence level for risk adjustment (e.g., 0.75 for 75th percentile)"
    )
    method: str = Field(
        ...,
        description="Risk adjustment calculation method (cost_of_capital, quantile, margin_over_current_estimate)"
    )
    cost_of_capital_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Cost of capital rate if using cost_of_capital method"
    )
    diversification_benefit: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Diversification benefit factor (0=no benefit, 1=full diversification)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "confidence_level": 0.75,
                "method": "cost_of_capital",
                "cost_of_capital_rate": 0.06,
                "diversification_benefit": 0.15
            }
        }
    )


class IFRSInput(BaseModel):
    """Input schema for IFRS 17 accrual calculation.
    
    Standardized input following platform conventions.
    All IFRS accrual requests must conform to this schema.
    """
    
    # Contract identification
    contract_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique insurance contract identifier"
    )
    contract_type: ContractType = Field(
        ...,
        description="IFRS 17 contract classification"
    )
    inception_date: date = Field(
        ...,
        description="Contract inception date"
    )
    coverage_period_months: int = Field(
        ...,
        ge=1,
        le=1200,
        description="Total coverage period in months"
    )
    
    # Valuation date
    valuation_date: date = Field(
        ...,
        description="Date for which to calculate accrual (reporting date)"
    )
    
    # Contract terms
    total_premium: Decimal = Field(
        ...,
        ge=0,
        description="Total contractual premium amount"
    )
    sum_insured: Decimal = Field(
        ...,
        ge=0,
        description="Sum insured / coverage amount"
    )
    coverage_unit: CoverageUnit = Field(
        ...,
        description="Unit of coverage for release pattern"
    )
    
    # Cash flow projections
    cash_flow_patterns: List[CashFlowPattern] = Field(
        ...,
        min_length=1,
        description="Expected cash flow patterns over contract life"
    )
    
    # Discount rates
    discount_curve_type: DiscountCurve = Field(
        ...,
        description="Type of discount curve to use"
    )
    discount_rates: Dict[int, float] = Field(
        ...,
        description="Discount rates by period (months) - e.g., {12: 0.03, 24: 0.035}"
    )
    
    # Risk adjustment
    risk_adjustment: RiskAdjustment = Field(
        ...,
        description="Risk adjustment parameters for non-financial risk"
    )
    
    # Contractual Service Margin (CSM)
    initial_csm: Optional[Decimal] = Field(
        default=None,
        description="Initial CSM at inception (if contract already exists, otherwise calculated)"
    )
    csm_amortization_pattern: str = Field(
        default="coverage_units",
        description="CSM amortization pattern (coverage_units, time_based, claims_based)"
    )
    
    # Acquisition costs
    acquisition_costs: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Insurance acquisition cash flows (commissions, underwriting, etc.)"
    )
    
    # Onerous contract test (for PAA)
    perform_onerous_test: bool = Field(
        default=True,
        description="Whether to perform onerous contract test (required for PAA)"
    )
    
    # Experience adjustments
    actual_claims_to_date: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Actual claims paid/incurred to valuation date"
    )
    actual_expenses_to_date: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Actual expenses incurred to valuation date"
    )
    
    # Context
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="Currency code (ISO 4217)"
    )
    reporting_entity: str = Field(
        ...,
        description="Reporting entity identifier"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context or metadata"
    )

    @field_validator('valuation_date')
    @classmethod
    def valuation_after_inception(cls, v: date, info) -> date:
        """Validate valuation date is on or after inception."""
        if 'inception_date' in info.data and v < info.data['inception_date']:
            raise ValueError('Valuation date cannot be before contract inception')
        return v

    @field_validator('discount_rates')
    @classmethod
    def validate_discount_rates(cls, v: Dict[int, float]) -> Dict[int, float]:
        """Validate discount rates are reasonable."""
        for period, rate in v.items():
            if period < 0:
                raise ValueError(f'Discount period {period} cannot be negative')
            if not -0.1 <= rate <= 0.5:  # -10% to 50% annual rate
                raise ValueError(f'Discount rate {rate} for period {period} is outside reasonable range')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "contract_id": "IFRS-CNT-2026-001",
                "contract_type": "paa",
                "inception_date": "2026-01-01",
                "coverage_period_months": 12,
                "valuation_date": "2026-01-20",
                "total_premium": "1200.00",
                "sum_insured": "100000.00",
                "coverage_unit": "time_based",
                "cash_flow_patterns": [
                    {
                        "period_months": 1,
                        "expected_premium": "100.00",
                        "expected_claims": "60.00",
                        "expected_expenses": "15.00",
                        "probability_weight": 1.0
                    }
                ],
                "discount_curve_type": "risk_free",
                "discount_rates": {
                    "12": 0.03,
                    "24": 0.035,
                    "36": 0.038
                },
                "risk_adjustment": {
                    "confidence_level": 0.75,
                    "method": "cost_of_capital",
                    "cost_of_capital_rate": 0.06,
                    "diversification_benefit": 0.15
                },
                "csm_amortization_pattern": "coverage_units",
                "acquisition_costs": "50.00",
                "perform_onerous_test": True,
                "actual_claims_to_date": "0.00",
                "actual_expenses_to_date": "5.00",
                "currency": "USD",
                "reporting_entity": "BDR-Insurance-US",
                "metadata": {
                    "product_line": "auto",
                    "portfolio": "personal_lines"
                }
            }
        }
    )


class LiabilityComponent(BaseModel):
    """Individual liability component breakdown."""
    
    component_name: str = Field(
        ...,
        description="Name of liability component"
    )
    amount: Decimal = Field(
        ...,
        description="Component amount"
    )
    description: str = Field(
        ...,
        description="Description of this component"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "component_name": "present_value_future_claims",
                "amount": "850.00",
                "description": "Present value of expected future claims"
            }
        }
    )


class CSMMovement(BaseModel):
    """Contractual Service Margin movement analysis."""
    
    opening_balance: Decimal = Field(
        ...,
        description="CSM balance at start of period"
    )
    accretion_of_interest: Decimal = Field(
        default=Decimal("0.00"),
        description="Interest accretion on CSM"
    )
    changes_in_estimates: Decimal = Field(
        default=Decimal("0.00"),
        description="Changes due to estimate updates"
    )
    experience_adjustments: Decimal = Field(
        default=Decimal("0.00"),
        description="Experience adjustments"
    )
    amortization: Decimal = Field(
        ...,
        description="CSM amortization for the period (negative)"
    )
    closing_balance: Decimal = Field(
        ...,
        description="CSM balance at end of period"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "opening_balance": "200.00",
                "accretion_of_interest": "0.50",
                "changes_in_estimates": "0.00",
                "experience_adjustments": "-5.00",
                "amortization": "-16.67",
                "closing_balance": "178.83"
            }
        }
    )


class IFRSOutput(BaseModel):
    """Output schema for IFRS 17 accrual calculation.
    
    Standardized output following platform conventions.
    Matches the standard decision output format.
    """
    
    # Standard platform fields
    decision_id: str = Field(
        ...,
        description="Unique identifier for this IFRS calculation"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this calculation was performed"
    )
    
    # Reference data
    contract_id: str = Field(
        ...,
        description="Reference to input contract ID"
    )
    valuation_date: date = Field(
        ...,
        description="Valuation/reporting date"
    )
    
    # Liability for Remaining Coverage (LRC)
    lrc_total: Decimal = Field(
        ...,
        description="Total Liability for Remaining Coverage"
    )
    lrc_excluding_loss_component: Decimal = Field(
        ...,
        description="LRC excluding any loss component"
    )
    loss_component: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        description="Loss component for onerous contracts"
    )
    
    # Liability for Incurred Claims (LIC)
    lic_total: Decimal = Field(
        ...,
        description="Total Liability for Incurred Claims"
    )
    
    # LRC Components breakdown
    lrc_components: List[LiabilityComponent] = Field(
        default_factory=list,
        description="Detailed breakdown of LRC components"
    )
    
    # Contractual Service Margin
    csm_balance: Decimal = Field(
        ...,
        description="Contractual Service Margin balance at valuation date"
    )
    csm_movement: Optional[CSMMovement] = Field(
        default=None,
        description="CSM movement analysis for the period"
    )
    
    # Risk Adjustment
    risk_adjustment_amount: Decimal = Field(
        ...,
        description="Risk adjustment for non-financial risk"
    )
    
    # Present values
    present_value_future_cash_outflows: Decimal = Field(
        ...,
        description="PV of expected future cash outflows (claims + expenses)"
    )
    present_value_future_cash_inflows: Decimal = Field(
        ...,
        description="PV of expected future cash inflows (premiums)"
    )
    
    # Coverage metrics
    coverage_units_total: Decimal = Field(
        ...,
        description="Total coverage units over contract life"
    )
    coverage_units_provided: Decimal = Field(
        ...,
        description="Coverage units provided to valuation date"
    )
    coverage_units_remaining: Decimal = Field(
        ...,
        description="Coverage units remaining after valuation date"
    )
    
    # Onerous contract test
    is_onerous: bool = Field(
        ...,
        description="Whether contract is onerous (loss-making)"
    )
    onerous_test_details: Optional[str] = Field(
        default=None,
        description="Details of onerous contract test if performed"
    )
    
    # Income statement impact
    insurance_revenue: Decimal = Field(
        ...,
        description="Insurance revenue for the period"
    )
    insurance_service_expense: Decimal = Field(
        ...,
        description="Insurance service expense for the period"
    )
    insurance_service_result: Decimal = Field(
        ...,
        description="Insurance service result (revenue - expense)"
    )
    
    # Reconciliation
    opening_liability: Decimal = Field(
        ...,
        description="Total insurance contract liability at period start"
    )
    closing_liability: Decimal = Field(
        ...,
        description="Total insurance contract liability at period end"
    )
    
    # Confidence and validation
    calculation_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in calculation accuracy (0-1)"
    )
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="Any validation warnings or notes"
    )
    
    # Human-in-the-loop
    requires_actuarial_review: bool = Field(
        ...,
        description="Whether actuarial review is required"
    )
    review_reason: Optional[str] = Field(
        default=None,
        description="Reason why actuarial review is required"
    )
    
    # Audit trail
    calculation_method: str = Field(
        ...,
        description="Calculation method used (PAA, BBA, VFA)"
    )
    model_version: str = Field(
        ...,
        description="Version of IFRS calculation engine used"
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
                "decision_id": "IFRS-CALC-2026-001",
                "timestamp": "2026-01-20T15:30:00Z",
                "contract_id": "IFRS-CNT-2026-001",
                "valuation_date": "2026-01-20",
                "lrc_total": "1050.00",
                "lrc_excluding_loss_component": "1050.00",
                "loss_component": "0.00",
                "lic_total": "0.00",
                "lrc_components": [
                    {
                        "component_name": "present_value_future_claims",
                        "amount": "700.00",
                        "description": "PV of expected future claims"
                    },
                    {
                        "component_name": "present_value_future_expenses",
                        "amount": "175.00",
                        "description": "PV of expected future expenses"
                    },
                    {
                        "component_name": "risk_adjustment",
                        "amount": "75.00",
                        "description": "Risk adjustment for non-financial risk"
                    },
                    {
                        "component_name": "csm",
                        "amount": "100.00",
                        "description": "Contractual Service Margin"
                    }
                ],
                "csm_balance": "100.00",
                "risk_adjustment_amount": "75.00",
                "present_value_future_cash_outflows": "875.00",
                "present_value_future_cash_inflows": "1150.00",
                "coverage_units_total": "12.00",
                "coverage_units_provided": "0.67",
                "coverage_units_remaining": "11.33",
                "is_onerous": False,
                "insurance_revenue": "100.00",
                "insurance_service_expense": "75.00",
                "insurance_service_result": "25.00",
                "opening_liability": "1100.00",
                "closing_liability": "1050.00",
                "calculation_confidence": 0.95,
                "validation_warnings": [],
                "requires_actuarial_review": False,
                "calculation_method": "PAA",
                "model_version": "ifrs-engine-v1.2.0",
                "processing_time_ms": 156.7,
                "currency": "USD",
                "metadata": {
                    "discount_curve_source": "treasury_curve_2026_01_20",
                    "assumptions_version": "2026_Q1"
                }
            }
        }
    )
