"""Fraud Detection Service - Human-in-the-Loop Decision Service.

This service orchestrates fraud detection decisions with mandatory human oversight
for high-risk cases.
"""

from typing import Optional
from datetime import datetime
import uuid

from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import require_permission


class FraudDetectionService:
    """Service layer for fraud detection with human-in-the-loop governance."""

    def __init__(self):
        self.decision_orchestrator = DecisionOrchestrator()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()

    @require_permission("fraud:detect")
    def detect_fraud(
        self,
        claim_data: dict,
        user_id: str,
        override_human_review: bool = False,
    ) -> dict:
        """Execute fraud detection with human-in-the-loop governance.

        Args:
            claim_data: Claim data for fraud analysis
            user_id: ID of user requesting the decision
            override_human_review: If True, skip human review (requires elevated permissions)

        Returns:
            Fraud detection result with human review requirements
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create decision context
        context = DecisionContext(
            decision_id=decision_id,
            decision_type=DecisionType.BOUNDED,  # Fraud detection is bounded decision
            user_id=user_id,
            metadata={
                "claim_id": claim_data.get("claim_id"),
                "claim_amount": claim_data.get("claim_amount"),
            },
        )

        # Log decision start
        self.audit_logger.log_decision_start(context)

        try:
            # TODO(platform): Integrate actual fraud detection engine
            # For now, return placeholder structure
            result = {
                "decision_id": decision_id,
                "timestamp": start_time,
                "risk_level": "medium",
                "fraud_score": 0.45,
                "indicators": [],
                "requires_investigation": False,
                "investigation_reason": None,
                "processing_time_ms": 0,
            }

            # Apply policy rules to determine human review requirements
            requires_review = self._requires_human_review(
                claim_data, result, override_human_review
            )

            if requires_review:
                result["requires_investigation"] = True
                result["investigation_reason"] = self._get_review_reason(
                    claim_data, result
                )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time

            # Log successful decision
            self.audit_logger.log_decision_complete(
                decision_id=decision_id,
                outcome=result["risk_level"],
                requires_human_review=result["requires_investigation"],
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
        self, claim_data: dict, result: dict, override: bool
    ) -> bool:
        """Determine if human investigation is required based on policy rules.

        Human review is MANDATORY for:
        - High fraud scores (>0.7)
        - High-value claims (>$100,000)
        - Multiple fraud indicators (>3)
        - Critical risk level
        """
        if override:
            return False

        # Policy rule: High fraud score requires investigation
        if result["fraud_score"] > 0.7:
            return True

        # Policy rule: High-value claims require investigation
        if claim_data.get("claim_amount", 0) > 100000:
            return True

        # Policy rule: Multiple indicators require investigation
        if len(result.get("indicators", [])) > 3:
            return True

        # Policy rule: Critical risk requires investigation
        if result["risk_level"] == "critical":
            return True

        return False

    def _get_review_reason(self, claim_data: dict, result: dict) -> str:
        """Generate human-readable reason for requiring investigation."""
        reasons = []

        if result["fraud_score"] > 0.7:
            reasons.append(f"High fraud score ({result['fraud_score']:.2f})")

        if claim_data.get("claim_amount", 0) > 100000:
            reasons.append(
                f"High-value claim (${claim_data.get('claim_amount', 0):,.2f})"
            )

        if len(result.get("indicators", [])) > 3:
            reasons.append(
                f"Multiple fraud indicators ({len(result.get('indicators', []))})"
            )

        if result["risk_level"] == "critical":
            reasons.append("Critical risk level")

        return "; ".join(reasons) if reasons else "Policy-based investigation required"


# Public API
__all__ = ["FraudDetectionService"]
