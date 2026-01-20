"""Reinsurance Pricing Engine - Core Business Logic

Extracted from Hugging Face Space: reinsurance-pricing
Consolidation Date: January 20, 2026

This module contains the core business logic for reinsurance treaty pricing,
including catastrophe modeling, layer analysis, and market positioning.

NOTE(platform): Extracted business logic only. UI components remain in HF Space.
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from .schemas import (
    ReinsuranceInput,
    ReinsuranceOutput,
    TreatyType,
    LayerAnalysis,
    CatastropheExposure,
)


class ReinsurancePricingEngine:
    """Core reinsurance pricing engine extracted from HF Space.
    
    This engine performs:
    - Treaty pricing calculation
    - Catastrophe exposure modeling
    - Layer analysis and optimization
    - Market rate comparison
    - ROL (Rate on Line) calculation
    """

    # Base rates by treaty type (as percentage of limit)
    BASE_RATES = {
        TreatyType.QUOTA_SHARE: Decimal("0.15"),  # 15%
        TreatyType.SURPLUS: Decimal("0.12"),  # 12%
        TreatyType.EXCESS_OF_LOSS: Decimal("0.08"),  # 8%
        TreatyType.CATASTROPHE: Decimal("0.20"),  # 20%
        TreatyType.STOP_LOSS: Decimal("0.25"),  # 25%
    }

    # Catastrophe load factors by region
    CAT_LOAD_FACTORS = {
        "california": Decimal("1.50"),  # High earthquake risk
        "florida": Decimal("1.60"),  # High hurricane risk
        "gulf_coast": Decimal("1.45"),  # Hurricane risk
        "midwest": Decimal("1.20"),  # Tornado risk
        "northeast": Decimal("1.10"),  # Moderate risk
        "other": Decimal("1.00"),  # Base risk
    }

    def __init__(self):
        """Initialize the reinsurance pricing engine."""
        self.version = "1.0.0"

    def price_treaty(self, reinsurance_input: ReinsuranceInput) -> ReinsuranceOutput:
        """Main reinsurance pricing function.
        
        Args:
            reinsurance_input: Reinsurance pricing input data
            
        Returns:
            ReinsuranceOutput with complete pricing analysis
        """
        # Calculate base premium
        base_premium = self._calculate_base_premium(
            reinsurance_input.treaty_type,
            reinsurance_input.limit,
        )
        
        # Calculate catastrophe exposure
        cat_exposure = self._calculate_cat_exposure(
            reinsurance_input.limit,
            reinsurance_input.attachment_point,
            reinsurance_input.geographic_region,
            reinsurance_input.is_cat_treaty,
        )
        
        # Apply catastrophe load
        cat_adjusted_premium = self._apply_cat_load(
            base_premium,
            cat_exposure,
            reinsurance_input.is_cat_treaty,
        )
        
        # Calculate expected loss
        expected_loss = self._calculate_expected_loss(
            reinsurance_input.expected_loss_ratio,
            reinsurance_input.limit,
        )
        
        # Calculate Rate on Line (ROL)
        rol = self._calculate_rol(
            cat_adjusted_premium,
            reinsurance_input.limit,
        )
        
        # Perform layer analysis
        layer_analysis = self._analyze_layer(
            reinsurance_input.attachment_point,
            reinsurance_input.limit,
            expected_loss,
            cat_adjusted_premium,
        )
        
        # Compare to market rates
        market_comparison = self._compare_to_market(
            rol,
            reinsurance_input.treaty_type,
            reinsurance_input.is_cat_treaty,
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            layer_analysis,
            market_comparison,
            expected_loss,
            cat_adjusted_premium,
        )
        
        # Determine if actuary review is required
        requires_review, review_reason = self._determine_review_requirement(
            reinsurance_input.limit,
            reinsurance_input.is_cat_treaty,
            expected_loss,
            cat_adjusted_premium,
        )
        
        return ReinsuranceOutput(
            decision_id=f"reins_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            base_premium=base_premium,
            catastrophe_load=cat_adjusted_premium - base_premium,
            total_premium=cat_adjusted_premium,
            expected_loss=expected_loss,
            rate_on_line=rol,
            layer_analysis=layer_analysis,
            catastrophe_exposure=cat_exposure,
            market_comparison=market_comparison,
            recommendation=recommendation,
            requires_actuary_review=requires_review,
            review_reason=review_reason,
            confidence=self._calculate_confidence(reinsurance_input),
            model_version=self.version,
        )

    def _calculate_base_premium(
        self,
        treaty_type: TreatyType,
        limit: Decimal,
    ) -> Decimal:
        """Calculate base premium before adjustments."""
        base_rate = self.BASE_RATES[treaty_type]
        premium = limit * base_rate
        
        return premium.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_cat_exposure(
        self,
        limit: Decimal,
        attachment_point: Decimal,
        geographic_region: str,
        is_cat_treaty: bool,
    ) -> CatastropheExposure:
        """Calculate catastrophe exposure."""
        # Get regional load factor
        region_key = geographic_region.lower().replace(" ", "_")
        load_factor = self.CAT_LOAD_FACTORS.get(region_key, Decimal("1.00"))
        
        # Calculate PML (Probable Maximum Loss) - simplified
        # In reality, this would use sophisticated cat models
        pml_100_year = limit * Decimal("0.30") * load_factor
        pml_250_year = limit * Decimal("0.50") * load_factor
        
        # Calculate expected annual loss from catastrophes
        if is_cat_treaty:
            expected_annual_loss = limit * Decimal("0.05") * load_factor
        else:
            expected_annual_loss = limit * Decimal("0.02") * load_factor
        
        return CatastropheExposure(
            pml_100_year=pml_100_year.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            pml_250_year=pml_250_year.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            expected_annual_loss=expected_annual_loss.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            geographic_concentration=geographic_region,
        )

    def _apply_cat_load(
        self,
        base_premium: Decimal,
        cat_exposure: CatastropheExposure,
        is_cat_treaty: bool,
    ) -> Decimal:
        """Apply catastrophe load to base premium."""
        if not is_cat_treaty:
            # Minimal cat load for non-cat treaties
            return base_premium * Decimal("1.10")
        
        # Calculate cat load as percentage of expected annual loss
        cat_load = cat_exposure.expected_annual_loss * Decimal("1.50")
        
        adjusted_premium = base_premium + cat_load
        
        return adjusted_premium.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_expected_loss(
        self,
        expected_loss_ratio: float,
        limit: Decimal,
    ) -> Decimal:
        """Calculate expected loss."""
        expected_loss = limit * Decimal(str(expected_loss_ratio))
        
        return expected_loss.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_rol(
        self,
        premium: Decimal,
        limit: Decimal,
    ) -> float:
        """Calculate Rate on Line (ROL).
        
        ROL = Premium / Limit
        """
        if limit == 0:
            return 0.0
        
        rol = (premium / limit) * Decimal("100")
        return float(rol.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

    def _analyze_layer(
        self,
        attachment_point: Decimal,
        limit: Decimal,
        expected_loss: Decimal,
        premium: Decimal,
    ) -> LayerAnalysis:
        """Analyze the reinsurance layer."""
        # Calculate layer characteristics
        exhaustion_point = attachment_point + limit
        
        # Calculate loss ratio
        loss_ratio = float((expected_loss / premium * Decimal("100")).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )) if premium > 0 else 0.0
        
        # Determine layer attractiveness
        if loss_ratio < 50:
            attractiveness = "highly_attractive"
        elif loss_ratio < 70:
            attractiveness = "attractive"
        elif loss_ratio < 90:
            attractiveness = "acceptable"
        else:
            attractiveness = "unattractive"
        
        # Calculate burning cost (simplified)
        burning_cost = expected_loss
        
        return LayerAnalysis(
            attachment_point=attachment_point,
            limit=limit,
            exhaustion_point=exhaustion_point,
            expected_loss_ratio=loss_ratio,
            burning_cost=burning_cost,
            layer_attractiveness=attractiveness,
        )

    def _compare_to_market(
        self,
        rol: float,
        treaty_type: TreatyType,
        is_cat_treaty: bool,
    ) -> str:
        """Compare pricing to market rates."""
        # Market ROL benchmarks (simplified)
        market_benchmarks = {
            TreatyType.QUOTA_SHARE: {"low": 12, "high": 18},
            TreatyType.SURPLUS: {"low": 10, "high": 15},
            TreatyType.EXCESS_OF_LOSS: {"low": 6, "high": 12},
            TreatyType.CATASTROPHE: {"low": 15, "high": 30},
            TreatyType.STOP_LOSS: {"low": 20, "high": 35},
        }
        
        benchmark = market_benchmarks[treaty_type]
        
        if rol < benchmark["low"]:
            return f"Below market (market range: {benchmark['low']}-{benchmark['high']}%)"
        elif rol > benchmark["high"]:
            return f"Above market (market range: {benchmark['low']}-{benchmark['high']}%)"
        else:
            return f"Within market range ({benchmark['low']}-{benchmark['high']}%)"

    def _generate_recommendation(
        self,
        layer_analysis: LayerAnalysis,
        market_comparison: str,
        expected_loss: Decimal,
        premium: Decimal,
    ) -> str:
        """Generate pricing recommendation."""
        recommendations = []
        
        # Layer attractiveness
        if layer_analysis.layer_attractiveness == "highly_attractive":
            recommendations.append(
                "Layer is highly attractive with strong profitability potential."
            )
        elif layer_analysis.layer_attractiveness == "attractive":
            recommendations.append(
                "Layer presents good risk-adjusted returns."
            )
        elif layer_analysis.layer_attractiveness == "acceptable":
            recommendations.append(
                "Layer is acceptable but monitor closely for adverse development."
            )
        else:
            recommendations.append(
                "Layer presents elevated risk. Consider declining or repricing."
            )
        
        # Market comparison
        if "Below market" in market_comparison:
            recommendations.append(
                "Pricing is below market rates. Consider increasing premium or declining."
            )
        elif "Above market" in market_comparison:
            recommendations.append(
                "Pricing is above market rates. May face competitive pressure."
            )
        else:
            recommendations.append(
                "Pricing is competitive with current market conditions."
            )
        
        # Loss ratio
        if layer_analysis.expected_loss_ratio > 80:
            recommendations.append(
                "High expected loss ratio requires careful consideration."
            )
        
        return " ".join(recommendations)

    def _determine_review_requirement(
        self,
        limit: Decimal,
        is_cat_treaty: bool,
        expected_loss: Decimal,
        premium: Decimal,
    ) -> tuple[bool, Optional[str]]:
        """Determine if actuary review is required."""
        # Large limits always require review
        if limit > Decimal("100000000"):
            return True, f"Large limit: ${limit:,.2f}"
        
        # Catastrophe treaties require review
        if is_cat_treaty:
            return True, "Catastrophe treaty requires actuary approval"
        
        # High expected loss ratio requires review
        if premium > 0:
            loss_ratio = float((expected_loss / premium) * Decimal("100"))
            if loss_ratio > 70:
                return True, f"High expected loss ratio: {loss_ratio:.1f}%"
        
        # Significant deviation from market
        # This would be more sophisticated in production
        
        return False, None

    def _calculate_confidence(
        self,
        reinsurance_input: ReinsuranceInput,
    ) -> float:
        """Calculate confidence in the pricing."""
        confidence = 0.80  # Base confidence
        
        # Reduce confidence for catastrophe treaties (more uncertainty)
        if reinsurance_input.is_cat_treaty:
            confidence -= 0.10
        
        # Reduce confidence for very large limits
        if reinsurance_input.limit > Decimal("500000000"):
            confidence -= 0.10
        
        # Reduce confidence for high-risk regions
        high_risk_regions = ["california", "florida", "gulf coast"]
        if any(region in reinsurance_input.geographic_region.lower() for region in high_risk_regions):
            confidence -= 0.05
        
        return max(0.5, min(0.95, confidence))
