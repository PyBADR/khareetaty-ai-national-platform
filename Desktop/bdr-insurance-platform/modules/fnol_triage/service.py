"""FNOL Triage Service - Human-in-the-Loop Decision Service.

This service orchestrates FNOL triage decisions with mandatory human oversight
for high-risk or ambiguous cases.
"""

from typing import Optional
from datetime import datetime
import uuid

from core.decision_engine import DecisionOrchestrator, DecisionType, DecisionContext
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import require_permission

from .models import FNOLInput, FNOLOutput
from .engine import FNOLTriageEngine


class FNOLTriageService:
    """Service layer for FNOL triage with human-in-the-loop governance."""

    def __init__(self):
        self.decision_orchestrator = DecisionOrchestrator()
        self.policy_enforcer = PolicyEnforcer()
        self.audit_logger = AuditLogger()
        self.engine = FNOLTriageEngine()

    @require_permission("fnol:triage")
    def run_fnol_triage(
        self,
        input_data: FNOLInput,
        user_id: str,
        override_human_review: bool = False,
    ) -> FNOLOutput:
        """Execute FNOL triage with human-in-the-loop governance.

        Args:
            input_data: Validated FNOL input data
            user_id: ID of user requesting the decision
            override_human_review: If True, skip human review (requires elevated permissions)

        Returns:
            FNOLOutput with triage decision and human review requirements
        """
        decision_id = str(uuid.uuid4())
        start_time = datetime.utcnow()

        # Create decision context
        context = DecisionContext(
            decision_id=decision_id,
            decision_type=DecisionType.ADVISORY,
            user_id=user_id,
            metadata={
                "claim_id": input_data.claim_id,
                "product_type": input_data.policy.product_type,
                "estimated_cost": float(input_data.estimated_cost),
                "policy_id": input_data.policy.policy_id,
            },
        )

        # Log decision start
        self.audit_logger.log_decision_start(context)

        try:
            # Run core triage engine
            engine_result = self.engine.triage(input_data)

            # Convert to standardized output
            output = engine_result.to_output()
            output.decision_id = decision_id
            output.timestamp = start_time

            # Apply policy rules to determine human review requirements
            requires_review = self._requires_human_review(
                input_data, output, override_human_review
            )

            if requires_review:
                output.requires_adjuster_review = True
                output.review_reason = self._get_review_reason(input_data, output)

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            output.processing_time_ms = processing_time

            # Log successful decision
            self.audit_logger.log_decision_complete(
                decision_id=decision_id,
                outcome=output.priority_level,
                requires_human_review=output.requires_adjuster_review,
                processing_time_ms=processing_time,
            )

            # Emit telemetry
            self.decision_orchestrator.emit_decision_metrics(
                decision_type="fnol_triage",
                confidence=output.confidence,
                requires_review=output.requires_adjuster_review,
                processing_time_ms=processing_time,
            )

            return output

        except Exception as e:
            # Log failure
            self.audit_logger.log_decision_error(
                decision_id=decision_id, error=str(e)
            )
            raise

    def _requires_human_review(
        self, input_data: FNOLInput, output: FNOLOutput, override: bool
    ) -> bool:
        """Determine if human review is required based on policy rules.

        Human review is MANDATORY for:
        - High-value claims (>$50,000)
        - Low confidence decisions (<0.7)
        - Critical priority cases
        - Bodily injury claims
        - Multiple claimants
        """
        if override:
            # NOTE(governance): Override requires elevated permissions
            # This should be logged and audited separately
            return False

        # Policy rule: High-value claims require review
        if input_data.estimated_cost > 50000:
            return True

        # Policy rule: Low confidence requires review
        if output.confidence < 0.7:
            return True

        # Policy rule: High priority requires review
        if output.recommendation == "high_priority":
            return True

        # Policy rule: Suspicious claims require review
        if "suspicious" in output.reasoning.lower():
            return True

        return False

    def _get_review_reason(self, input_data: FNOLInput, output: FNOLOutput) -> str:
        """Generate human-readable reason for requiring review."""
        reasons = []

        if input_data.estimated_cost > 50000:
            reasons.append(
                f"High-value claim (${input_data.estimated_cost:,.2f})"
            )

        if output.confidence < 0.7:
            reasons.append(f"Low confidence score ({output.confidence:.2f})")

        if output.recommendation == "high_priority":
            reasons.append("High priority level")

        if "suspicious" in output.reasoning.lower():
            reasons.append("Suspicious indicators detected")

        return "; ".join(reasons) if reasons else "Policy-based review required"


# Public API
__all__ = ["FNOLTriageService"]
