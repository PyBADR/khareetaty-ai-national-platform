"""Underwriting Scoring Engine - Core Business Logic

Extracted from Hugging Face Space: underwriting-scoring
Consolidation Date: January 20, 2026

This module contains the core business logic for underwriting risk assessment,
including risk scoring, tier classification, and premium calculation.

NOTE(platform): Extracted business logic only. UI components remain in HF Space.
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from .schemas import (
    UnderwritingInput,
    UnderwritingOutput,
    RiskTier,
    RiskFactor,
)


class UnderwritingEngine:
    """Core underwriting scoring engine extracted from HF Space.
    
    This engine performs:
    - Multi-factor risk assessment
    - Risk tier classification
    - Premium calculation and adjustment
    - Underwriting recommendations
    """

    # Risk scoring weights
    RISK_WEIGHTS = {
        "demographics": 0.25,
        "credit_score": 0.20,
        "claims_history": 0.30,
        "coverage_amount": 0.15,
        "occupation": 0.10,
    }

    # Base premium rates by coverage type (per $1000 of coverage)
    BASE_RATES = {
        "life": Decimal("0.50"),
        "health": Decimal("2.00"),
        "auto": Decimal("1.50"),
        "property": Decimal("0.80"),
        "liability": Decimal("1.20"),
    }

    # Risk tier multipliers
    TIER_MULTIPLIERS = {
        RiskTier.PREFERRED: Decimal("0.80"),
        RiskTier.STANDARD: Decimal("1.00"),
        RiskTier.SUBSTANDARD: Decimal("1.40"),
        RiskTier.DECLINED: Decimal("0.00"),  # Not offered
    }

    def __init__(self):
        """Initialize the underwriting engine."""
        self.version = "1.0.0"

    def assess_risk(self, underwriting_input: UnderwritingInput) -> UnderwritingOutput:
        """Main underwriting assessment function.
        
        Args:
            underwriting_input: Underwriting input data
            
        Returns:
            UnderwritingOutput with complete risk assessment
        """
        # Collect risk factors
        risk_factors = []
        risk_factors.extend(self._assess_demographics(underwriting_input))
        risk_factors.extend(self._assess_credit(underwriting_input))
        risk_factors.extend(self._assess_claims_history(underwriting_input))
        risk_factors.extend(self._assess_coverage_amount(underwriting_input))
        risk_factors.extend(self._assess_occupation(underwriting_input))
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(risk_factors)
        
        # Determine risk tier
        risk_tier = self._determine_risk_tier(risk_score, risk_factors)
        
        # Calculate premium
        base_premium = self._calculate_base_premium(
            underwriting_input.coverage_type,
            underwriting_input.coverage_amount,
        )
        adjusted_premium = self._calculate_adjusted_premium(
            base_premium,
            risk_tier,
            risk_factors,
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_tier, risk_score)
        
        # Determine if underwriter review is required
        requires_review, review_reason = self._determine_review_requirement(
            risk_tier,
            risk_score,
            underwriting_input.coverage_amount,
        )
        
        return UnderwritingOutput(
            decision_id=f"uw_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            risk_score=risk_score,
            risk_tier=risk_tier,
            risk_factors=risk_factors,
            base_premium=base_premium,
            adjusted_premium=adjusted_premium,
            premium_adjustment_percentage=self._calculate_adjustment_percentage(
                base_premium, adjusted_premium
            ),
            recommendation=recommendation,
            requires_underwriter_review=requires_review,
            review_reason=review_reason,
            confidence=self._calculate_confidence(risk_factors),
            model_version=self.version,
        )

    def _assess_demographics(self, underwriting_input: UnderwritingInput) -> List[RiskFactor]:
        """Assess demographic risk factors."""
        factors = []
        
        if not underwriting_input.demographics:
            return factors
        
        demo = underwriting_input.demographics
        
        # Age assessment
        if demo.age < 25:
            factors.append(
                RiskFactor(
                    factor_name="Young Age",
                    impact="negative",
                    weight=0.15,
                    description=f"Applicant age {demo.age} is below 25",
                )
            )
        elif demo.age > 65:
            factors.append(
                RiskFactor(
                    factor_name="Senior Age",
                    impact="negative",
                    weight=0.10,
                    description=f"Applicant age {demo.age} is above 65",
                )
            )
        elif 35 <= demo.age <= 55:
            factors.append(
                RiskFactor(
                    factor_name="Prime Age",
                    impact="positive",
                    weight=0.05,
                    description=f"Applicant age {demo.age} is in prime range",
                )
            )
        
        # Gender assessment (for certain coverage types)
        if underwriting_input.coverage_type.lower() == "life":
            if demo.gender.lower() == "female":
                factors.append(
                    RiskFactor(
                        factor_name="Gender - Life Expectancy",
                        impact="positive",
                        weight=0.03,
                        description="Statistical life expectancy advantage",
                    )
                )
        
        # Smoking status
        if demo.is_smoker:
            factors.append(
                RiskFactor(
                    factor_name="Tobacco Use",
                    impact="negative",
                    weight=0.25,
                    description="Applicant is a tobacco user",
                )
            )
        
        return factors

    def _assess_credit(self, underwriting_input: UnderwritingInput) -> List[RiskFactor]:
        """Assess credit-related risk factors."""
        factors = []
        
        if underwriting_input.credit_score is None:
            factors.append(
                RiskFactor(
                    factor_name="No Credit Score",
                    impact="negative",
                    weight=0.10,
                    description="Credit score not available",
                )
            )
            return factors
        
        credit_score = underwriting_input.credit_score
        
        # Excellent credit
        if credit_score >= 750:
            factors.append(
                RiskFactor(
                    factor_name="Excellent Credit",
                    impact="positive",
                    weight=0.15,
                    description=f"Credit score {credit_score} is excellent",
                )
            )
        # Good credit
        elif credit_score >= 700:
            factors.append(
                RiskFactor(
                    factor_name="Good Credit",
                    impact="positive",
                    weight=0.08,
                    description=f"Credit score {credit_score} is good",
                )
            )
        # Fair credit
        elif credit_score >= 650:
            factors.append(
                RiskFactor(
                    factor_name="Fair Credit",
                    impact="neutral",
                    weight=0.00,
                    description=f"Credit score {credit_score} is fair",
                )
            )
        # Poor credit
        else:
            factors.append(
                RiskFactor(
                    factor_name="Poor Credit",
                    impact="negative",
                    weight=0.20,
                    description=f"Credit score {credit_score} is below acceptable threshold",
                )
            )
        
        return factors

    def _assess_claims_history(self, underwriting_input: UnderwritingInput) -> List[RiskFactor]:
        """Assess claims history risk factors."""
        factors = []
        
        if not underwriting_input.claims_history:
            # No claims history is generally positive
            factors.append(
                RiskFactor(
                    factor_name="No Claims History",
                    impact="positive",
                    weight=0.10,
                    description="No previous claims on record",
                )
            )
            return factors
        
        history = underwriting_input.claims_history
        
        # Multiple claims
        if history.total_claims > 3:
            factors.append(
                RiskFactor(
                    factor_name="High Claims Frequency",
                    impact="negative",
                    weight=0.25,
                    description=f"{history.total_claims} claims in history",
                )
            )
        elif history.total_claims > 1:
            factors.append(
                RiskFactor(
                    factor_name="Moderate Claims Frequency",
                    impact="negative",
                    weight=0.12,
                    description=f"{history.total_claims} claims in history",
                )
            )
        
        # Recent claims
        if history.claims_last_3_years > 0:
            factors.append(
                RiskFactor(
                    factor_name="Recent Claims Activity",
                    impact="negative",
                    weight=0.15,
                    description=f"{history.claims_last_3_years} claims in last 3 years",
                )
            )
        
        # Large claims
        if history.largest_claim_amount and history.largest_claim_amount > Decimal("50000"):
            factors.append(
                RiskFactor(
                    factor_name="Large Previous Claim",
                    impact="negative",
                    weight=0.10,
                    description=f"Previous claim of ${history.largest_claim_amount:,.2f}",
                )
            )
        
        return factors

    def _assess_coverage_amount(self, underwriting_input: UnderwritingInput) -> List[RiskFactor]:
        """Assess coverage amount risk factors."""
        factors = []
        
        coverage = underwriting_input.coverage_amount
        
        # Very high coverage
        if coverage > Decimal("1000000"):
            factors.append(
                RiskFactor(
                    factor_name="High Coverage Amount",
                    impact="negative",
                    weight=0.12,
                    description=f"Coverage amount ${coverage:,.2f} requires additional scrutiny",
                )
            )
        
        return factors

    def _assess_occupation(self, underwriting_input: UnderwritingInput) -> List[RiskFactor]:
        """Assess occupation risk factors."""
        factors = []
        
        if not underwriting_input.occupation:
            return factors
        
        occupation_lower = underwriting_input.occupation.lower()
        
        # High-risk occupations
        high_risk_occupations = [
            "construction", "mining", "logging", "fishing",
            "pilot", "firefighter", "police"
        ]
        if any(risk_occ in occupation_lower for risk_occ in high_risk_occupations):
            factors.append(
                RiskFactor(
                    factor_name="High-Risk Occupation",
                    impact="negative",
                    weight=0.18,
                    description=f"Occupation '{underwriting_input.occupation}' is high-risk",
                )
            )
        
        # Low-risk occupations
        low_risk_occupations = [
            "teacher", "accountant", "engineer", "doctor",
            "lawyer", "manager", "analyst"
        ]
        if any(low_occ in occupation_lower for low_occ in low_risk_occupations):
            factors.append(
                RiskFactor(
                    factor_name="Low-Risk Occupation",
                    impact="positive",
                    weight=0.08,
                    description=f"Occupation '{underwriting_input.occupation}' is low-risk",
                )
            )
        
        return factors

    def _calculate_risk_score(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate overall risk score (0-1)."""
        # Start at neutral (0.5)
        score = 0.5
        
        for factor in risk_factors:
            if factor.impact == "positive":
                score -= factor.weight
            elif factor.impact == "negative":
                score += factor.weight
            # neutral factors don't change score
        
        # Clamp to 0-1 range
        return max(0.0, min(1.0, round(score, 3)))

    def _determine_risk_tier(self, risk_score: float, risk_factors: List[RiskFactor]) -> RiskTier:
        """Determine risk tier based on score and factors."""
        # Check for automatic decline factors
        decline_factors = [
            f for f in risk_factors
            if f.impact == "negative" and f.weight >= 0.25
        ]
        if len(decline_factors) >= 2:
            return RiskTier.DECLINED
        
        # Score-based tiers
        if risk_score <= 0.35:
            return RiskTier.PREFERRED
        elif risk_score <= 0.55:
            return RiskTier.STANDARD
        elif risk_score <= 0.75:
            return RiskTier.SUBSTANDARD
        else:
            return RiskTier.DECLINED

    def _calculate_base_premium(
        self,
        coverage_type: str,
        coverage_amount: Decimal,
    ) -> Decimal:
        """Calculate base premium before adjustments."""
        # Get base rate
        base_rate = self.BASE_RATES.get(
            coverage_type.lower(),
            Decimal("1.00"),
        )
        
        # Calculate premium (rate per $1000 of coverage)
        premium = (coverage_amount / Decimal("1000")) * base_rate
        
        return premium.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_adjusted_premium(
        self,
        base_premium: Decimal,
        risk_tier: RiskTier,
        risk_factors: List[RiskFactor],
    ) -> Decimal:
        """Calculate adjusted premium based on risk tier."""
        # Apply tier multiplier
        multiplier = self.TIER_MULTIPLIERS[risk_tier]
        adjusted = base_premium * multiplier
        
        return adjusted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_adjustment_percentage(
        self,
        base_premium: Decimal,
        adjusted_premium: Decimal,
    ) -> float:
        """Calculate percentage adjustment from base to adjusted premium."""
        if base_premium == 0:
            return 0.0
        
        adjustment = ((adjusted_premium - base_premium) / base_premium) * Decimal("100")
        return float(adjustment.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))

    def _generate_recommendation(self, risk_tier: RiskTier, risk_score: float) -> str:
        """Generate underwriting recommendation."""
        recommendations = {
            RiskTier.PREFERRED: (
                "Approve with preferred rates. Applicant presents low risk profile "
                "and qualifies for best available pricing."
            ),
            RiskTier.STANDARD: (
                "Approve with standard rates. Applicant presents acceptable risk profile "
                "within normal underwriting guidelines."
            ),
            RiskTier.SUBSTANDARD: (
                "Approve with substandard rates. Applicant presents elevated risk requiring "
                "premium adjustment. Consider additional underwriting requirements."
            ),
            RiskTier.DECLINED: (
                "Decline application. Applicant's risk profile exceeds acceptable thresholds. "
                "Consider alternative coverage options or risk mitigation."
            ),
        }
        return recommendations[risk_tier]

    def _determine_review_requirement(
        self,
        risk_tier: RiskTier,
        risk_score: float,
        coverage_amount: Decimal,
    ) -> tuple[bool, Optional[str]]:
        """Determine if underwriter review is required."""
        # Always review declined applications
        if risk_tier == RiskTier.DECLINED:
            return True, "Declined applications require underwriter review"
        
        # Review substandard risks
        if risk_tier == RiskTier.SUBSTANDARD:
            return True, "Substandard risk tier requires underwriter approval"
        
        # Review large coverage amounts
        if coverage_amount > Decimal("1000000"):
            return True, f"Large coverage amount: ${coverage_amount:,.2f}"
        
        # Review borderline scores
        if 0.45 <= risk_score <= 0.55:
            return True, "Borderline risk score requires underwriter judgment"
        
        return False, None

    def _calculate_confidence(self, risk_factors: List[RiskFactor]) -> float:
        """Calculate confidence in the assessment."""
        # Base confidence
        confidence = 0.85
        
        # More factors = higher confidence
        if len(risk_factors) >= 5:
            confidence += 0.10
        elif len(risk_factors) <= 2:
            confidence -= 0.15
        
        return max(0.5, min(0.99, confidence))
