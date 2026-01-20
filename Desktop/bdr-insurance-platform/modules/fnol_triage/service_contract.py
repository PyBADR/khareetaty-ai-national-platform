"""FNOL Triage Service - Contract-Compliant Implementation.

This service uses the formal Decision Contract (DecisionRequest/DecisionResponse).
This is the NEW standard - all modules must migrate to this pattern.

Extracted from: deevo-fnol-fast-triage Hugging Face Space
Contract Version: 2.0.0
"""

from typing import Dict, Any
from datetime import datetime
from decimal import Decimal
import time

from core.decision_engine import (
    DecisionRequest,
    DecisionResponse,
    AuditMetadata,
    BoundaryResult,
    BoundaryCheck,
    BoundaryType,
    create_boundary_result,
    Explainability,
    DecisionFactor,
    ScoredSignal,
    Evidence,
    DecisionTypeEnum,
)
from core.security import require_permission
from core.audit_logging import AuditLogger

from .engine import FNOLTriageEngine
from .models import FNOLInput


class FNOLTriageServiceContract:
    """Contract-compliant FNOL Triage Service.
    
    This service:
    - Accepts DecisionRequest
    - Returns DecisionResponse (ONLY valid return type)
    - Enforces boundaries
    - Provides mandatory explainability
    - Includes full audit trail
    """

    MODULE_NAME = "fnol_triage"
    MODULE_VERSION = "2.0.0"

    def __init__(self):
        self.engine = FNOLTriageEngine()
        self.audit_logger = AuditLogger()

    @require_permission("fnol:triage")
    def execute(self, request: DecisionRequest) -> DecisionResponse:
        """Execute FNOL triage with formal decision contract.
        
        Args:
            request: DecisionRequest with input_data containing FNOLInput fields
        
        Returns:
            DecisionResponse with complete contract compliance
        """
        start_time = time.time()
        
        # Log decision start
        self.audit_logger.log_decision_start(
            decision_id=request.decision_id,
            module=self.MODULE_NAME,
            user_id=request.user_id,
        )
        
        try:
            # Parse input data into FNOLInput model
            fnol_input = self._parse_input(request.input_data)
            
            # Run the triage engine
            engine_result = self.engine.triage(fnol_input)
            
            # Perform boundary checks
            boundaries = self._check_boundaries(fnol_input, engine_result)
            
            # Generate explainability
            explainability = self._generate_explainability(
                fnol_input, engine_result, boundaries
            )
            
            # Determine human review requirement
            human_review_required = self._requires_human_review(
                request, engine_result, boundaries
            )
            human_review_reason = self._get_review_reason(
                engine_result, boundaries
            ) if human_review_required else None
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Create audit metadata
            audit_metadata = AuditMetadata(
                decision_id=request.decision_id,
                timestamp=datetime.utcnow(),
                module_name=self.MODULE_NAME,
                module_version=self.MODULE_VERSION,
                user_id=request.user_id,
                session_id=request.session_id,
                processing_time_ms=processing_time_ms,
                environment="production",
                audit_trail={
                    "claim_id": fnol_input.claim_id,
                    "estimated_cost": float(fnol_input.estimated_cost),
                    "policy_id": fnol_input.policy.policy_id,
                },
            )
            
            # Build decision output
            decision_output = {
                "claim_id": engine_result.claim_id,
                "priority": engine_result.priority,
                "risk_category": engine_result.risk_category,
                "confidence": engine_result.confidence,
                "next_steps": engine_result.next_steps,
                "suspicious_indicators": engine_result.suspicious_indicators,
                "estimated_cost": float(fnol_input.estimated_cost),
            }
            
            # Determine actionability
            actionable = (
                request.decision_type == DecisionTypeEnum.BOUNDED
                and boundaries.all_passed
                and not human_review_required
            )
            
            # Create the response
            response = DecisionResponse(
                decision_id=request.decision_id,
                decision_type=request.decision_type,
                decision_output=decision_output,
                boundaries=boundaries,
                explainability=explainability,
                audit_metadata=audit_metadata,
                human_review_required=human_review_required,
                human_review_reason=human_review_reason,
                actionable=actionable,
                errors=[],
            )
            
            # Log decision completion
            self.audit_logger.log_decision_complete(
                decision_id=request.decision_id,
                outcome=decision_output,
                human_review_required=human_review_required,
            )
            
            return response
            
        except Exception as e:
            # Log error
            self.audit_logger.log_decision_error(
                decision_id=request.decision_id,
                error=str(e),
            )
            raise

    def _parse_input(self, input_data: Dict[str, Any]) -> FNOLInput:
        """Parse input data into FNOLInput model.
        
        Args:
            input_data: Raw input data dictionary
        
        Returns:
            Validated FNOLInput instance
        """
        # TODO(platform): Add proper validation and error handling
        return FNOLInput(**input_data)

    def _check_boundaries(self, fnol_input: FNOLInput, engine_result) -> BoundaryResult:
        """Perform boundary checks for FNOL triage.
        
        Args:
            fnol_input: Validated input
            engine_result: Result from triage engine
        
        Returns:
            BoundaryResult with all checks
        """
        checks = []
        
        # Check 1: High-value claim threshold
        high_value_threshold = 50000.0
        claim_amount = float(fnol_input.estimated_cost)
        checks.append(
            BoundaryCheck(
                boundary_type=BoundaryType.MONETARY,
                name="High Value Claim Threshold",
                threshold=high_value_threshold,
                actual_value=claim_amount,
                passed=claim_amount <= high_value_threshold,
                reason=(
                    f"Claim amount ${claim_amount:,.2f} exceeds threshold ${high_value_threshold:,.2f}"
                    if claim_amount > high_value_threshold
                    else f"Claim amount ${claim_amount:,.2f} within threshold"
                ),
            )
        )
        
        # Check 2: Confidence threshold
        min_confidence = 0.7
        checks.append(
            BoundaryCheck(
                boundary_type=BoundaryType.CONFIDENCE,
                name="Minimum Confidence Threshold",
                threshold=min_confidence,
                actual_value=engine_result.confidence,
                passed=engine_result.confidence >= min_confidence,
                reason=(
                    f"Confidence {engine_result.confidence:.2f} below threshold {min_confidence:.2f}"
                    if engine_result.confidence < min_confidence
                    else f"Confidence {engine_result.confidence:.2f} meets threshold"
                ),
            )
        )
        
        # Check 3: Risk category
        checks.append(
            BoundaryCheck(
                boundary_type=BoundaryType.RISK,
                name="Risk Category Check",
                threshold=None,
                actual_value=None,
                passed=engine_result.risk_category != "RED",
                reason=(
                    "High-risk (RED) category requires human review"
                    if engine_result.risk_category == "RED"
                    else f"Risk category {engine_result.risk_category} acceptable"
                ),
            )
        )
        
        # Check 4: Suspicious indicators
        max_suspicious_indicators = 2
        num_indicators = len(engine_result.suspicious_indicators)
        checks.append(
            BoundaryCheck(
                boundary_type=BoundaryType.COMPLEXITY,
                name="Suspicious Indicators Threshold",
                threshold=float(max_suspicious_indicators),
                actual_value=float(num_indicators),
                passed=num_indicators <= max_suspicious_indicators,
                reason=(
                    f"{num_indicators} suspicious indicators exceed threshold of {max_suspicious_indicators}"
                    if num_indicators > max_suspicious_indicators
                    else f"{num_indicators} suspicious indicators within threshold"
                ),
            )
        )
        
        return create_boundary_result(
            checks=checks,
            human_review_reason=None,  # Will be computed from failed checks
        )

    def _generate_explainability(
        self, fnol_input: FNOLInput, engine_result, boundaries: BoundaryResult
    ) -> Explainability:
        """Generate mandatory explainability for the decision.
        
        Args:
            fnol_input: Input data
            engine_result: Engine result
            boundaries: Boundary check results
        
        Returns:
            Complete Explainability payload
        """
        # Build key factors
        key_factors = [
            DecisionFactor(
                name="claim_amount",
                value=float(fnol_input.estimated_cost),
                weight=0.8,
                impact="negative" if float(fnol_input.estimated_cost) > 50000 else "neutral",
                description=f"Claim amount of ${float(fnol_input.estimated_cost):,.2f}",
            ),
            DecisionFactor(
                name="risk_category",
                value=engine_result.risk_category,
                weight=0.9,
                impact="negative" if engine_result.risk_category == "RED" else "neutral",
                description=f"Risk category assessed as {engine_result.risk_category}",
            ),
            DecisionFactor(
                name="confidence",
                value=engine_result.confidence,
                weight=0.7,
                impact="positive" if engine_result.confidence >= 0.8 else "neutral",
                description=f"Model confidence: {engine_result.confidence:.2%}",
            ),
        ]
        
        # Build scored signals
        scored_signals = []
        for indicator in engine_result.suspicious_indicators:
            scored_signals.append(
                ScoredSignal(
                    signal_name=indicator,
                    score=0.8,  # TODO(platform): Get actual scores from engine
                    threshold=0.7,
                    triggered=True,
                    evidence=f"Indicator '{indicator}' detected in claim",
                )
            )
        
        # Build evidence
        evidence = [
            Evidence(
                category="claim_details",
                items=[
                    f"Claim ID: {fnol_input.claim_id}",
                    f"Estimated cost: ${float(fnol_input.estimated_cost):,.2f}",
                    f"Policy ID: {fnol_input.policy.policy_id}",
                    f"Product type: {fnol_input.policy.product_type}",
                ],
                confidence=1.0,
                source="input_data",
            ),
            Evidence(
                category="triage_result",
                items=[
                    f"Priority: {engine_result.priority}",
                    f"Risk category: {engine_result.risk_category}",
                    f"Confidence: {engine_result.confidence:.2%}",
                    f"Suspicious indicators: {len(engine_result.suspicious_indicators)}",
                ],
                confidence=engine_result.confidence,
                source="triage_engine",
            ),
        ]
        
        # Generate summary
        summary = self._generate_summary(engine_result, boundaries)
        
        return Explainability(
            summary=summary,
            key_factors=key_factors,
            scored_signals=scored_signals,
            evidence=evidence,
            confidence_score=engine_result.confidence,
            model_version=self.MODULE_VERSION,
            explanation_metadata={
                "total_factors": len(key_factors),
                "triggered_signals": len(scored_signals),
                "boundary_checks": len(boundaries.checks),
                "failed_boundaries": len(boundaries.failed_checks),
            },
        )

    def _generate_summary(self, engine_result, boundaries: BoundaryResult) -> str:
        """Generate human-readable summary.
        
        Args:
            engine_result: Engine result
            boundaries: Boundary results
        
        Returns:
            Human-readable summary string
        """
        if boundaries.all_passed and engine_result.risk_category == "GREEN":
            return f"Standard {engine_result.priority} priority claim with no red flags"
        elif engine_result.risk_category == "RED":
            return f"High-risk claim requires immediate adjuster review"
        elif not boundaries.all_passed:
            return f"Claim exceeds boundaries: {boundaries.get_failure_summary()}"
        else:
            return f"{engine_result.priority} priority claim with {engine_result.risk_category} risk level"

    def _requires_human_review(
        self, request: DecisionRequest, engine_result, boundaries: BoundaryResult
    ) -> bool:
        """Determine if human review is required.
        
        Args:
            request: Original request
            engine_result: Engine result
            boundaries: Boundary results
        
        Returns:
            True if human review is required
        """
        # Override if requested (requires elevated permissions)
        if request.override_boundaries:
            return False
        
        # Advisory decisions always require human review
        if request.decision_type == DecisionTypeEnum.ADVISORY:
            return True
        
        # Boundary failures require human review
        if not boundaries.all_passed:
            return True
        
        # High-risk category requires human review
        if engine_result.risk_category == "RED":
            return True
        
        # High priority requires human review
        if engine_result.priority == "high":
            return True
        
        return False

    def _get_review_reason(self, engine_result, boundaries: BoundaryResult) -> str:
        """Get human-readable reason for review requirement.
        
        Args:
            engine_result: Engine result
            boundaries: Boundary results
        
        Returns:
            Human-readable reason string
        """
        reasons = []
        
        if not boundaries.all_passed:
            reasons.append(boundaries.get_failure_summary())
        
        if engine_result.risk_category == "RED":
            reasons.append("High-risk category detected")
        
        if engine_result.priority == "high":
            reasons.append("High priority claim")
        
        if len(engine_result.suspicious_indicators) > 0:
            reasons.append(
                f"{len(engine_result.suspicious_indicators)} suspicious indicator(s) detected"
            )
        
        return "; ".join(reasons) if reasons else "Human review required by policy"


# Convenience function for backward compatibility
def run_fnol_triage_contract(
    claim_id: str,
    estimated_cost: Decimal,
    policy_data: Dict[str, Any],
    customer_data: Dict[str, Any],
    incident_data: Dict[str, Any],
    user_id: str,
    decision_type: DecisionTypeEnum = DecisionTypeEnum.BOUNDED,
) -> DecisionResponse:
    """Convenience function to run FNOL triage with contract.
    
    Args:
        claim_id: Unique claim identifier
        estimated_cost: Estimated claim cost
        policy_data: Policy information
        customer_data: Customer information
        incident_data: Incident details
        user_id: User requesting the decision
        decision_type: Type of decision (default: BOUNDED)
    
    Returns:
        DecisionResponse with complete contract compliance
    """
    service = FNOLTriageServiceContract()
    
    request = DecisionRequest(
        decision_type=decision_type,
        module_name="fnol_triage",
        input_data={
            "claim_id": claim_id,
            "estimated_cost": estimated_cost,
            "policy": policy_data,
            "customer": customer_data,
            "incident": incident_data,
        },
        user_id=user_id,
    )
    
    return service.execute(request)
