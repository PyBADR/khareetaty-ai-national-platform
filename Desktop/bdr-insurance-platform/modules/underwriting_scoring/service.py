"""Underwriting Scoring Service - Human-in-the-Loop Decision Service.

This service orchestrates underwriting risk scoring with mandatory human oversight
for high-risk or borderline cases.
"""

from typing import Optional
from datetime import datetime
import uuid

from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import require_permission


class UnderwritingScoringService:
    """Service layer for underwriting scoring with human-in-the-loop governance."""

    def __init__(self):
        self.decision_orchestrator = DecisionOrchestrator()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()

    @require_permission("underwriting:score")
    def score_application(
        self,
        application_data: dict,
        user_id: str,
        override_human_review: bool = False,
    ) -> dict:
        """Execute underwriting scoring with human-in-the-loop governance.

        Args:
            application_data: Application data for underwriting assessment
            user_id: ID of user requesting the decision
            override_human_review: If True, skip human review (requires elevated permissions)

        Returns:
            Underwriting score result with human review requirements
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create decision context
        context = DecisionContext(
            decision_id=decision_id,
            decision_type=DecisionType.ADVISORY,  # Underwriting is advisory
            user_id=user_id,
            metadata={
                "application_id": application_data.get("application_id"),
                "coverage_amount": application_data.get("coverage_amount"),
            },
        )

        # Log decision start
        self.audit_logger.log_decision_start(context)

        try:
            # TODO(platform): Integrate actual underwriting scoring engine
            # For now, return placeholder structure
            result = {
                "decision_id": decision_id,
                "timestamp": start_time,
                "risk_score": 0.5,
                "risk_tier": "standard",
                "recommended_premium": 0,
                "requires_underwriter_review": False,
                "review_reason": None,
                "processing_time_ms": 0,
            }

            # Apply policy rules to determine human review requirements
            requires_review = self._requires_human_review(
                application_data, result, override_human_review
            )

            if requires_review:
                result["requires_underwriter_review"] = True
                result["review_reason"] = self._get_review_reason(
                    application_data, result
                )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time

            # Log successful decision
            self.audit_logger.log_decision_complete(
                decision_id=decision_id,
                outcome=result["risk_tier"],
                requires_human_review=result["requires_underwriter_review"],
                processing_time_ms=processing_time,
            )

            return result

        except Exception as e:
            # Log failure
            self.audit_logger.log_decision_error(
                decision_id=decision_id, error=str(e)
            )
            raise

    def _requires_human_review(
        self, application_data: dict, result: dict, override: bool
    ) -> bool:
        """Determine if underwriter review is required based on policy rules.

        Human review is MANDATORY for:
        - High-risk scores (>0.7)
        - Large coverage amounts (>$1M)
        - Substandard risk tier
        - Borderline scores (0.45-0.55)
        """
        if override:
            return False

        # Policy rule: High-risk scores require review
        if result["risk_score"] > 0.7:
            return True

        # Policy rule: Large coverage requires review
        if application_data.get("coverage_amount", 0) > 1_000_000:
            return True

        # Policy rule: Substandard risk requires review
        if result["risk_tier"] == "substandard":
            return True

        # Policy rule: Borderline scores require review
        if 0.45 <= result["risk_score"] <= 0.55:
            return True

        return False

    def _get_review_reason(self, application_data: dict, result: dict) -> str:
        """Generate human-readable reason for requiring underwriter review."""
        reasons = []

        if result["risk_score"] > 0.7:
            reasons.append(f"High risk score ({result['risk_score']:.2f})")

        if application_data.get("coverage_amount", 0) > 1_000_000:
            reasons.append(
                f"Large coverage amount (${application_data.get('coverage_amount', 0):,.2f})"
            )

        if result["risk_tier"] == "substandard":
            reasons.append("Substandard risk tier")

        if 0.45 <= result["risk_score"] <= 0.55:
            reasons.append(f"Borderline risk score ({result['risk_score']:.2f})")

        return "; ".join(reasons) if reasons else "Policy-based review required"


# Public API
__all__ = ["UnderwritingScoringService"]