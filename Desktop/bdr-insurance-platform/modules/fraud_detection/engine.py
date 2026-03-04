"""Fraud Detection Engine - Core Business Logic

Extracted from Hugging Face Space: fraud-detection
Consolidation Date: January 20, 2026

This module contains the core business logic for fraud detection,
including risk scoring, indicator identification, and investigation routing.

NOTE(platform): Extracted business logic only. UI components remain in HF Space.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from .schemas import (
    FraudInput,
    FraudOutput,
    FraudIndicator,
    RiskLevel,
    IndicatorType,
    IndicatorSeverity,
)


class FraudDetectionEngine:
    """Core fraud detection engine extracted from HF Space.
    
    This engine performs:
    - Multi-factor fraud risk scoring
    - Fraud indicator identification
    - Investigation priority determination
    - Pattern-based anomaly detection
    """

    # Risk scoring weights
    RISK_WEIGHTS = {
        "claim_characteristics": 0.30,
        "claimant_history": 0.25,
        "behavioral_patterns": 0.25,
        "external_data": 0.20,
    }

    # Thresholds
    HIGH_VALUE_THRESHOLD = Decimal("100000")
    SUSPICIOUS_VELOCITY_DAYS = 90
    SUSPICIOUS_VELOCITY_COUNT = 3

    def __init__(self):
        """Initialize the fraud detection engine."""
        self.version = "1.0.0"

    def detect_fraud(self, fraud_input: FraudInput) -> FraudOutput:
        """Main fraud detection function.
        
        Args:
            fraud_input: Fraud detection input data
            
        Returns:
            FraudOutput with risk score, indicators, and recommendations
        """
        # Collect all indicators
        indicators = []
        indicators.extend(self._check_claim_characteristics(fraud_input))
        indicators.extend(self._check_claimant_history(fraud_input))
        indicators.extend(self._check_behavioral_patterns(fraud_input))
        indicators.extend(self._check_external_data(fraud_input))
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(indicators)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score, len(indicators))
        
        # Generate investigation priority
        investigation_priority = self._determine_investigation_priority(
            risk_level, fraud_input.claim_amount
        )
        
        # Generate recommended actions
        recommended_actions = self._generate_recommended_actions(
            risk_level, indicators
        )
        
        # Determine if investigation is required
        requires_investigation = risk_level in [
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ] or len(indicators) >= 3
        
        # Generate investigation reason
        investigation_reason = None
        if requires_investigation:
            investigation_reason = self._generate_investigation_reason(
                risk_level, indicators
            )
        
        return FraudOutput(
            decision_id=f"fraud_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            risk_score=risk_score,
            risk_level=risk_level,
            indicators=indicators,
            requires_investigation=requires_investigation,
            investigation_reason=investigation_reason,
            investigation_priority=investigation_priority,
            recommended_actions=recommended_actions,
            confidence=self._calculate_confidence(indicators),
            model_version=self.version,
        )

    def _check_claim_characteristics(self, fraud_input: FraudInput) -> List[FraudIndicator]:
        """Check claim characteristics for fraud indicators."""
        indicators = []
        
        # High-value claim
        if fraud_input.claim_amount >= self.HIGH_VALUE_THRESHOLD:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.HIGH_VALUE_CLAIM,
                    severity=IndicatorSeverity.HIGH,
                    description=f"Claim amount ${fraud_input.claim_amount:,.2f} exceeds high-value threshold",
                    confidence=0.85,
                )
            )
        
        # Round number claim amount (potential estimation)
        if fraud_input.claim_amount % Decimal("10000") == 0 and fraud_input.claim_amount > 0:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.SUSPICIOUS_AMOUNT,
                    severity=IndicatorSeverity.MEDIUM,
                    description="Claim amount is a round number, suggesting estimation",
                    confidence=0.60,
                )
            )
        
        # Late reporting
        if fraud_input.incident_date:
            days_since_incident = (datetime.now().date() - fraud_input.incident_date).days
            if days_since_incident > 30:
                indicators.append(
                    FraudIndicator(
                        indicator_type=IndicatorType.LATE_REPORTING,
                        severity=IndicatorSeverity.MEDIUM,
                        description=f"Claim reported {days_since_incident} days after incident",
                        confidence=0.70,
                    )
                )
        
        # Suspicious description
        if fraud_input.claim_description:
            suspicious_keywords = [
                "lost", "stolen", "missing", "don't know", "not sure",
                "can't remember", "maybe", "think", "probably"
            ]
            found_keywords = [
                kw for kw in suspicious_keywords
                if kw in fraud_input.claim_description.lower()
            ]
            if found_keywords:
                indicators.append(
                    FraudIndicator(
                        indicator_type=IndicatorType.SUSPICIOUS_DESCRIPTION,
                        severity=IndicatorSeverity.MEDIUM,
                        description=f"Description contains suspicious keywords: {', '.join(found_keywords[:3])}",
                        confidence=0.65,
                    )
                )
        
        return indicators

    def _check_claimant_history(self, fraud_input: FraudInput) -> List[FraudIndicator]:
        """Check claimant history for fraud indicators."""
        indicators = []
        
        if not fraud_input.claimant_history:
            return indicators
        
        history = fraud_input.claimant_history
        
        # High claim frequency
        if history.total_claims > 5:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.HIGH_CLAIM_FREQUENCY,
                    severity=IndicatorSeverity.HIGH,
                    description=f"Claimant has {history.total_claims} previous claims",
                    confidence=0.80,
                )
            )
        
        # Previous fraud flags
        if history.previous_fraud_flags > 0:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.PRIOR_FRAUD_FLAG,
                    severity=IndicatorSeverity.CRITICAL,
                    description=f"Claimant has {history.previous_fraud_flags} previous fraud flags",
                    confidence=0.95,
                )
            )
        
        # Claim velocity (multiple claims in short period)
        if history.claims_last_90_days >= self.SUSPICIOUS_VELOCITY_COUNT:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.CLAIM_VELOCITY,
                    severity=IndicatorSeverity.HIGH,
                    description=f"{history.claims_last_90_days} claims in last 90 days",
                    confidence=0.85,
                )
            )
        
        return indicators

    def _check_behavioral_patterns(self, fraud_input: FraudInput) -> List[FraudIndicator]:
        """Check behavioral patterns for fraud indicators."""
        indicators = []
        
        # Policy recently purchased (< 30 days before incident)
        if fraud_input.policy_start_date and fraud_input.incident_date:
            days_between = (fraud_input.incident_date - fraud_input.policy_start_date).days
            if 0 <= days_between <= 30:
                indicators.append(
                    FraudIndicator(
                        indicator_type=IndicatorType.NEW_POLICY,
                        severity=IndicatorSeverity.HIGH,
                        description=f"Incident occurred {days_between} days after policy start",
                        confidence=0.75,
                    )
                )
        
        # Inconsistent contact information
        if fraud_input.contact_info_verified is False:
            indicators.append(
                FraudIndicator(
                    indicator_type=IndicatorType.INCONSISTENT_INFO,
                    severity=IndicatorSeverity.MEDIUM,
                    description="Contact information could not be verified",
                    confidence=0.70,
                )
            )
        
        return indicators

    def _check_external_data(self, fraud_input: FraudInput) -> List[FraudIndicator]:
        """Check external data sources for fraud indicators."""
        indicators = []
        
        # TODO(platform): Integrate with external fraud databases
        # TODO(platform): Check industry watchlists
        # TODO(platform): Verify third-party data sources
        
        return indicators

    def _calculate_risk_score(self, indicators: List[FraudIndicator]) -> float:
        """Calculate overall fraud risk score (0-1)."""
        if not indicators:
            return 0.0
        
        # Weight by severity and confidence
        severity_weights = {
            IndicatorSeverity.LOW: 0.25,
            IndicatorSeverity.MEDIUM: 0.50,
            IndicatorSeverity.HIGH: 0.75,
            IndicatorSeverity.CRITICAL: 1.0,
        }
        
        total_score = 0.0
        for indicator in indicators:
            severity_weight = severity_weights[indicator.severity]
            total_score += severity_weight * indicator.confidence
        
        # Normalize to 0-1 range
        # More indicators = higher risk, but with diminishing returns
        normalized_score = min(1.0, total_score / 3.0)
        
        return round(normalized_score, 3)

    def _determine_risk_level(self, risk_score: float, indicator_count: int) -> RiskLevel:
        """Determine risk level based on score and indicator count."""
        # Critical if very high score or many indicators
        if risk_score >= 0.8 or indicator_count >= 5:
            return RiskLevel.CRITICAL
        
        # High if high score or multiple indicators
        if risk_score >= 0.6 or indicator_count >= 3:
            return RiskLevel.HIGH
        
        # Medium if moderate score or some indicators
        if risk_score >= 0.3 or indicator_count >= 1:
            return RiskLevel.MEDIUM
        
        # Low otherwise
        return RiskLevel.LOW

    def _determine_investigation_priority(self, risk_level: RiskLevel, claim_amount: Decimal) -> str:
        """Determine investigation priority."""
        if risk_level == RiskLevel.CRITICAL:
            return "immediate"
        
        if risk_level == RiskLevel.HIGH:
            if claim_amount >= self.HIGH_VALUE_THRESHOLD:
                return "immediate"
            return "high"
        
        if risk_level == RiskLevel.MEDIUM:
            return "medium"
        
        return "low"

    def _generate_recommended_actions(self, risk_level: RiskLevel, indicators: List[FraudIndicator]) -> List[str]:
        """Generate recommended actions based on risk level."""
        actions = []
        
        if risk_level == RiskLevel.CRITICAL:
            actions.extend([
                "Immediately escalate to fraud investigation team",
                "Suspend claim processing pending investigation",
                "Request comprehensive documentation",
                "Conduct detailed claimant interview",
                "Verify all claim details with independent sources",
            ])
        elif risk_level == RiskLevel.HIGH:
            actions.extend([
                "Assign to senior fraud investigator",
                "Request additional documentation",
                "Conduct phone interview with claimant",
                "Verify incident details",
            ])
        elif risk_level == RiskLevel.MEDIUM:
            actions.extend([
                "Assign to fraud review queue",
                "Request standard documentation",
                "Verify basic claim details",
            ])
        else:
            actions.append("Process through standard claims workflow")
        
        # Add specific actions based on indicators
        indicator_types = {ind.indicator_type for ind in indicators}
        
        if IndicatorType.PRIOR_FRAUD_FLAG in indicator_types:
            actions.append("Review previous fraud investigation reports")
        
        if IndicatorType.HIGH_CLAIM_FREQUENCY in indicator_types:
            actions.append("Analyze pattern of previous claims")
        
        if IndicatorType.NEW_POLICY in indicator_types:
            actions.append("Verify policy application details")
        
        return actions

    def _generate_investigation_reason(self, risk_level: RiskLevel, indicators: List[FraudIndicator]) -> str:
        """Generate human-readable investigation reason."""
        if not indicators:
            return f"Risk level: {risk_level.value}"
        
        # Prioritize critical indicators
        critical_indicators = [
            ind for ind in indicators
            if ind.severity == IndicatorSeverity.CRITICAL
        ]
        
        if critical_indicators:
            return f"Critical fraud indicators detected: {critical_indicators[0].description}"
        
        # Otherwise, summarize all indicators
        indicator_count = len(indicators)
        return f"{indicator_count} fraud indicator(s) detected with {risk_level.value} risk level"

    def _calculate_confidence(self, indicators: List[FraudIndicator]) -> float:
        """Calculate confidence in fraud detection."""
        if not indicators:
            return 0.95  # High confidence in low-risk assessment
        
        # Average confidence of all indicators
        avg_confidence = sum(ind.confidence for ind in indicators) / len(indicators)
        
        # Adjust based on indicator count (more indicators = higher confidence)
        confidence_boost = min(0.1, len(indicators) * 0.02)
        
        return min(0.99, round(avg_confidence + confidence_boost, 3))
