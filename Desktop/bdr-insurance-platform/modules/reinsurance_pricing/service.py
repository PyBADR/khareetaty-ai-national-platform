"""Reinsurance Pricing Service - Human-in-the-Loop Decision Service.

This service orchestrates reinsurance treaty pricing with mandatory human oversight
for complex structures and material exposures.
"""

from typing import Optional
from datetime import datetime
import uuid

from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import require_permission


class ReinsurancePricingService:
    """Service layer for reinsurance pricing with human-in-the-loop governance."""

    def __init__(self):
        self.decision_orchestrator = DecisionOrchestrator()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()

    @require_permission("reinsurance:price")
    def price_treaty(
        self,
        treaty_data: dict,
        user_id: str,
        override_human_review: bool = False,
    ) -> dict:
        """Execute reinsurance treaty pricing with human-in-the-loop governance.

        Args:
            treaty_data: Treaty structure and exposure data
            user_id: ID of user requesting the pricing
            override_human_review: If True, skip human review (requires elevated permissions)

        Returns:
            Reinsurance pricing result with human review requirements
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create decision context
        context = DecisionContext(
            decision_id=decision_id,
            decision_type=DecisionType.SIMULATION,  # Pricing is simulation
            user_id=user_id,
            metadata={
                "treaty_id": treaty_data.get("treaty_id"),
                "treaty_type": treaty_data.get("treaty_type"),
                "limit": treaty_data.get("limit"),
            },
        )

        # Log decision start
        self.audit_logger.log_decision_start(context)

        try:
            # TODO(platform): Integrate actual reinsurance pricing engine
            # For now, return placeholder structure
            result = {
                "decision_id": decision_id,
                "timestamp": start_time,
                "technical_price": 0,
                "market_price": 0,
                "expected_loss": 0,
                "requires_actuary_review": False,
                "review_reason": None,
                "processing_time_ms": 0,
            }

            # Apply policy rules to determine human review requirements
            requires_review = self._requires_human_review(
                treaty_data, result, override_human_review
            )

            if requires_review:
                result["requires_actuary_review"] = True
                result["review_reason"] = self._get_review_reason(
                    treaty_data, result
                )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time

            # Log successful decision
            self.audit_logger.log_decision_complete(
                decision_id=decision_id,
                outcome="priced",
                requires_human_review=result["requires_actuary_review"],
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
        self, treaty_data: dict, result: dict, override: bool
    ) -> bool:
        """Determine if actuary review is required based on policy rules.

        Human review is MANDATORY for:
        - Large limits (>$100M)
        - Catastrophe treaties
        - High expected loss ratios (>70%)
        - Significant price deviations (>20% from market)
        """
        if override:
            return False

        # Policy rule: Large limits require review
        if treaty_data.get("limit", 0) > 100_000_000:
            return True

        # Policy rule: Catastrophe treaties require review
        if treaty_data.get("treaty_type", "").lower() in ["cat", "catastrophe"]:
            return True

        # Policy rule: High expected loss requires review
        technical_price = result.get("technical_price", 1)
        expected_loss = result.get("expected_loss", 0)
        if technical_price > 0 and (expected_loss / technical_price) > 0.7:
            return True

        # Policy rule: Significant price deviation requires review
        market_price = result.get("market_price", 0)
        if technical_price > 0 and market_price > 0:
            deviation = abs(technical_price - market_price) / market_price
            if deviation > 0.2:
                return True

        return False

    def _get_review_reason(self, treaty_data: dict, result: dict) -> str:
        """Generate human-readable reason for requiring actuary review."""
        reasons = []

        if treaty_data.get("limit", 0) > 100_000_000:
            reasons.append(
                f"Large limit (${treaty_data.get('limit', 0):,.2f})"
            )

        if treaty_data.get("treaty_type", "").lower() in ["cat", "catastrophe"]:
            reasons.append("Catastrophe treaty")

        technical_price = result.get("technical_price", 1)
        expected_loss = result.get("expected_loss", 0)
        if technical_price > 0 and (expected_loss / technical_price) > 0.7:
            loss_ratio = (expected_loss / technical_price) * 100
            reasons.append(f"High expected loss ratio ({loss_ratio:.1f}%)")

        market_price = result.get("market_price", 0)
        if technical_price > 0 and market_price > 0:
            deviation = abs(technical_price - market_price) / market_price
            if deviation > 0.2:
                deviation_pct = deviation * 100
                reasons.append(f"Price deviation from market ({deviation_pct:.1f}%)")

        return "; ".join(reasons) if reasons else "Policy-based review required"


# Public API
__all__ = ["ReinsurancePricingService"]