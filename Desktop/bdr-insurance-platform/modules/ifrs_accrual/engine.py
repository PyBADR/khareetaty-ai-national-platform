"""IFRS 17 Accrual Engine - Core Business Logic

Extracted from Hugging Face Space: ifrs17-accrual
Consolidation Date: January 20, 2026

This module contains the core business logic for IFRS 17 liability calculations,
including CSM computation, risk adjustments, and compliance validation.

NOTE(platform): Extracted business logic only. UI components remain in HF Space.
"""

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from .schemas import (
    IFRSInput,
    IFRSOutput,
    LiabilityComponent,
    CSMMovement,
    ComplianceStatus,
)


class IFRSAccrualEngine:
    """Core IFRS 17 accrual engine extracted from HF Space.
    
    This engine performs:
    - Present value of future cash flows (PVFCF) calculation
    - Risk adjustment computation
    - Contractual Service Margin (CSM) calculation
    - CSM movement tracking
    - Compliance validation
    """

    # Risk adjustment factors by coverage type
    RISK_ADJUSTMENT_FACTORS = {
        "life": Decimal("0.05"),  # 5%
        "health": Decimal("0.07"),  # 7%
        "property": Decimal("0.06"),  # 6%
        "liability": Decimal("0.08"),  # 8%
        "auto": Decimal("0.06"),  # 6%
    }

    # Discount rates by currency (simplified)
    DISCOUNT_RATES = {
        "USD": Decimal("0.045"),  # 4.5%
        "EUR": Decimal("0.025"),  # 2.5%
        "GBP": Decimal("0.040"),  # 4.0%
    }

    def __init__(self):
        """Initialize the IFRS 17 accrual engine."""
        self.version = "1.0.0"

    def calculate_accrual(self, ifrs_input: IFRSInput) -> IFRSOutput:
        """Main IFRS 17 accrual calculation function.
        
        Args:
            ifrs_input: IFRS 17 input data
            
        Returns:
            IFRSOutput with complete liability calculation
        """
        # Calculate present value of future cash flows
        pvfcf = self._calculate_pvfcf(
            ifrs_input.expected_claims,
            ifrs_input.expected_expenses,
            ifrs_input.coverage_period_years,
            ifrs_input.currency,
        )
        
        # Calculate risk adjustment
        risk_adjustment = self._calculate_risk_adjustment(
            pvfcf,
            ifrs_input.coverage_type,
            ifrs_input.risk_profile,
        )
        
        # Calculate CSM
        csm = self._calculate_csm(
            ifrs_input.premium,
            pvfcf,
            risk_adjustment,
        )
        
        # Calculate total liability
        total_liability = pvfcf + risk_adjustment + csm
        
        # Build liability components
        components = [
            LiabilityComponent(
                component_name="Present Value of Future Cash Flows",
                amount=pvfcf,
                percentage=self._calculate_percentage(pvfcf, total_liability),
            ),
            LiabilityComponent(
                component_name="Risk Adjustment",
                amount=risk_adjustment,
                percentage=self._calculate_percentage(risk_adjustment, total_liability),
            ),
            LiabilityComponent(
                component_name="Contractual Service Margin",
                amount=csm,
                percentage=self._calculate_percentage(csm, total_liability),
            ),
        ]
        
        # Calculate CSM movement (if previous CSM provided)
        csm_movement = None
        if ifrs_input.previous_csm is not None:
            csm_movement = self._calculate_csm_movement(
                ifrs_input.previous_csm,
                csm,
                ifrs_input.coverage_period_years,
            )
        
        # Validate compliance
        compliance_status, compliance_notes = self._validate_compliance(
            csm,
            risk_adjustment,
            total_liability,
        )
        
        # Determine if actuarial review is required
        requires_review, review_reason = self._determine_review_requirement(
            total_liability,
            risk_adjustment,
            compliance_status,
        )
        
        return IFRSOutput(
            decision_id=f"ifrs_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            total_liability=total_liability,
            liability_components=components,
            csm_amount=csm,
            csm_movement=csm_movement,
            risk_adjustment_amount=risk_adjustment,
            pvfcf_amount=pvfcf,
            compliance_status=compliance_status,
            compliance_notes=compliance_notes,
            requires_actuarial_review=requires_review,
            review_reason=review_reason,
            confidence=self._calculate_confidence(ifrs_input),
            model_version=self.version,
        )

    def _calculate_pvfcf(
        self,
        expected_claims: Decimal,
        expected_expenses: Decimal,
        coverage_period_years: int,
        currency: str,
    ) -> Decimal:
        """Calculate present value of future cash flows."""
        # Get discount rate
        discount_rate = self.DISCOUNT_RATES.get(currency, Decimal("0.04"))
        
        # Total expected cash flows
        total_cash_flows = expected_claims + expected_expenses
        
        # Discount to present value
        # PV = FV / (1 + r)^n
        discount_factor = (Decimal("1") + discount_rate) ** coverage_period_years
        pvfcf = total_cash_flows / discount_factor
        
        return pvfcf.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_risk_adjustment(
        self,
        pvfcf: Decimal,
        coverage_type: str,
        risk_profile: str,
    ) -> Decimal:
        """Calculate risk adjustment for non-financial risk."""
        # Get base risk adjustment factor
        base_factor = self.RISK_ADJUSTMENT_FACTORS.get(
            coverage_type.lower(),
            Decimal("0.06"),
        )
        
        # Adjust based on risk profile
        risk_multipliers = {
            "low": Decimal("0.8"),
            "medium": Decimal("1.0"),
            "high": Decimal("1.3"),
            "very_high": Decimal("1.6"),
        }
        multiplier = risk_multipliers.get(risk_profile.lower(), Decimal("1.0"))
        
        # Calculate risk adjustment
        risk_adjustment = pvfcf * base_factor * multiplier
        
        return risk_adjustment.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_csm(
        self,
        premium: Decimal,
        pvfcf: Decimal,
        risk_adjustment: Decimal,
    ) -> Decimal:
        """Calculate Contractual Service Margin.
        
        CSM = Premium - PVFCF - Risk Adjustment
        
        If negative (onerous contract), CSM = 0 and loss is recognized.
        """
        csm = premium - pvfcf - risk_adjustment
        
        # CSM cannot be negative (onerous contracts handled separately)
        if csm < 0:
            # TODO(platform): Log onerous contract for separate handling
            return Decimal("0.00")
        
        return csm.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _calculate_csm_movement(
        self,
        previous_csm: Decimal,
        current_csm: Decimal,
        coverage_period_years: int,
    ) -> CSMMovement:
        """Calculate CSM movement between periods."""
        # Opening balance
        opening_balance = previous_csm
        
        # Expected release (amortization)
        # Simplified: straight-line over coverage period
        expected_release = previous_csm / Decimal(str(coverage_period_years))
        
        # Changes in estimates
        changes_in_estimates = current_csm - (previous_csm - expected_release)
        
        # Closing balance
        closing_balance = current_csm
        
        return CSMMovement(
            opening_balance=opening_balance,
            expected_release=expected_release,
            changes_in_estimates=changes_in_estimates,
            closing_balance=closing_balance,
        )

    def _calculate_percentage(self, component: Decimal, total: Decimal) -> float:
        """Calculate percentage of component to total."""
        if total == 0:
            return 0.0
        
        percentage = float((component / total) * Decimal("100"))
        return round(percentage, 2)

    def _validate_compliance(
        self,
        csm: Decimal,
        risk_adjustment: Decimal,
        total_liability: Decimal,
    ) -> tuple[ComplianceStatus, List[str]]:
        """Validate IFRS 17 compliance."""
        notes = []
        
        # Check if CSM is non-negative
        if csm < 0:
            notes.append("WARNING: Negative CSM indicates onerous contract")
            return ComplianceStatus.NON_COMPLIANT, notes
        
        # Check if risk adjustment is reasonable (should be 5-15% of total)
        if total_liability > 0:
            ra_percentage = (risk_adjustment / total_liability) * Decimal("100")
            if ra_percentage < Decimal("3") or ra_percentage > Decimal("20"):
                notes.append(
                    f"Risk adjustment ({ra_percentage:.1f}%) outside typical range (3-20%)"
                )
                return ComplianceStatus.REQUIRES_REVIEW, notes
        
        # Check if total liability is positive
        if total_liability <= 0:
            notes.append("Total liability must be positive")
            return ComplianceStatus.NON_COMPLIANT, notes
        
        notes.append("All IFRS 17 compliance checks passed")
        return ComplianceStatus.COMPLIANT, notes

    def _determine_review_requirement(
        self,
        total_liability: Decimal,
        risk_adjustment: Decimal,
        compliance_status: ComplianceStatus,
    ) -> tuple[bool, Optional[str]]:
        """Determine if actuarial review is required."""
        # Always require review for non-compliant calculations
        if compliance_status == ComplianceStatus.NON_COMPLIANT:
            return True, "Non-compliant calculation requires actuarial review"
        
        # Require review for material liabilities (> $10M)
        if total_liability > Decimal("10000000"):
            return True, f"Material liability amount: ${total_liability:,.2f}"
        
        # Require review for high risk adjustments (> 20% of liability)
        if total_liability > 0:
            ra_percentage = (risk_adjustment / total_liability) * Decimal("100")
            if ra_percentage > Decimal("20"):
                return True, f"High risk adjustment: {ra_percentage:.1f}% of total liability"
        
        # Require review if compliance status is uncertain
        if compliance_status == ComplianceStatus.REQUIRES_REVIEW:
            return True, "Compliance status requires actuarial review"
        
        return False, None

    def _calculate_confidence(self, ifrs_input: IFRSInput) -> float:
        """Calculate confidence in the calculation."""
        confidence = 1.0
        
        # Reduce confidence for missing optional data
        if ifrs_input.previous_csm is None:
            confidence -= 0.05
        
        # Reduce confidence for very long coverage periods
        if ifrs_input.coverage_period_years > 10:
            confidence -= 0.10
        
        # Reduce confidence for high-risk profiles
        if ifrs_input.risk_profile.lower() in ["high", "very_high"]:
            confidence -= 0.10
        
        return max(0.5, min(1.0, confidence))
