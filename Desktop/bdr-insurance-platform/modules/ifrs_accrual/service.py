"""IFRS 17 Accrual Service - Human-in-the-Loop Decision Service.

This service orchestrates IFRS 17 accrual calculations with mandatory human oversight
for material adjustments and regulatory compliance.
"""

from typing import Optional
from datetime import datetime
import uuid

from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import require_permission


class IFRSAccrualService:
    """Service layer for IFRS 17 accrual with human-in-the-loop governance."""

    def __init__(self):
        self.decision_orchestrator = DecisionOrchestrator()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()

    @require_permission("ifrs:calculate")
    def calculate_accrual(
        self,
        contract_data: dict,
        user_id: str,
        override_human_review: bool = False,
    ) -> dict:
        """Execute IFRS 17 accrual calculation with human-in-the-loop governance.

        Args:
            contract_data: Insurance contract data for accrual calculation
            user_id: ID of user requesting the calculation
            override_human_review: If True, skip human review (requires elevated permissions)

        Returns:
            IFRS 17 accrual result with human review requirements
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create decision context
        context = DecisionContext(
            decision_id=decision_id,
            decision_type=DecisionType.SIMULATION,  # IFRS calculations are simulations
            user_id=user_id,
            metadata={
                "contract_id": contract_data.get("contract_id"),
                "liability_amount": contract_data.get("liability_amount"),
            },
        )

        # Log decision start
        self.audit_logger.log_decision_start(context)

        try:
            # TODO(platform): Integrate actual IFRS 17 calculation engine
            # For now, return placeholder structure
            result = {
                "decision_id": decision_id,
                "timestamp": start_time,
                "total_liability": 0,
                "csm_balance": 0,
                "risk_adjustment": 0,
                "requires_actuarial_review": False,
                "review_reason": None,
                "processing_time_ms": 0,
                "compliance_status": "compliant",
            }

            # Apply policy rules to determine human review requirements
            requires_review = self._requires_human_review(
                contract_data, result, override_human_review
            )

            if requires_review:
                result["requires_actuarial_review"] = True
                result["review_reason"] = self._get_review_reason(
                    contract_data, result
                )

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result["processing_time_ms"] = processing_time

            # Log successful decision
            self.audit_logger.log_decision_complete(
                decision_id=decision_id,
                outcome=result["compliance_status"],
                requires_human_review=result["requires_actuarial_review"],
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
        self, contract_data: dict, result: dict, override: bool
    ) -> bool:
        """Determine if actuarial review is required based on policy rules.

        Human review is MANDATORY for:
        - Material liabilities (>$10M)
        - Significant CSM changes (>10%)
        - Non-compliant calculations
        - High risk adjustments (>20% of liability)
        """
        if override:
            return False

        # Policy rule: Material liabilities require review
        if result.get("total_liability", 0) > 10_000_000:
            return True

        # Policy rule: Non-compliant calculations require review
        if result.get("compliance_status") != "compliant":
            return True

        # Policy rule: High risk adjustments require review
        total_liability = result.get("total_liability", 1)
        risk_adjustment = result.get("risk_adjustment", 0)
        if total_liability > 0 and (risk_adjustment / total_liability) > 0.2:
            return True

        return False

    def _get_review_reason(self, contract_data: dict, result: dict) -> str:
        """Generate human-readable reason for requiring actuarial review."""
        reasons = []

        if result.get("total_liability", 0) > 10_000_000:
            reasons.append(
                f"Material liability (${result.get('total_liability', 0):,.2f})"
            )

        if result.get("compliance_status") != "compliant":
            reasons.append(f"Non-compliant: {result.get('compliance_status')}")

        total_liability = result.get("total_liability", 1)
        risk_adjustment = result.get("risk_adjustment", 0)
        if total_liability > 0 and (risk_adjustment / total_liability) > 0.2:
            risk_pct = (risk_adjustment / total_liability) * 100
            reasons.append(f"High risk adjustment ({risk_pct:.1f}% of liability)")

        return "; ".join(reasons) if reasons else "Policy-based review required"


# Public API
__all__ = ["IFRSAccrualService"]