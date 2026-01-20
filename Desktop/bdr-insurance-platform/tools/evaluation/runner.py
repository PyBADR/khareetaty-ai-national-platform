"""
Evaluation Runner - Orchestrates Golden Case Execution

This module runs golden cases against decision modules and collects results.
It coordinates the execution pipeline and ensures proper isolation.

RUNNER = EXECUTION ENGINE
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import time
import traceback
import yaml

from .harness import (
    GoldenCase,
    CaseExecutionResult,
    ExpectedOutcome,
)
from core.decision_engine import (
    DecisionRequest,
    DecisionResponse,
)


class EvaluationRunner:
    """
    Orchestrates the execution of golden cases against decision modules.
    
    Responsibilities:
    - Load golden cases from YAML files
    - Execute cases against decision modules
    - Validate outcomes against expectations
    - Collect execution metrics
    - Handle errors gracefully
    """
    
    def __init__(
        self,
        module_name: str,
        decision_function: Callable[[DecisionRequest], DecisionResponse],
        golden_cases_dir: Optional[Path] = None,
    ):
        """
        Initialize the evaluation runner.
        
        Args:
            module_name: Name of the module being evaluated
            decision_function: Function that takes DecisionRequest and returns DecisionResponse
            golden_cases_dir: Directory containing golden case YAML files
        """
        self.module_name = module_name
        self.decision_function = decision_function
        
        if golden_cases_dir is None:
            # Default to tools/evaluation/golden_cases/{module_name}
            self.golden_cases_dir = Path(__file__).parent / "golden_cases" / module_name
        else:
            self.golden_cases_dir = Path(golden_cases_dir)
    
    def load_golden_cases(self) -> List[GoldenCase]:
        """
        Load all active golden cases for this module.
        
        Returns:
            List of GoldenCase objects
        
        Raises:
            FileNotFoundError: If golden cases directory doesn't exist
            ValueError: If YAML files are invalid
        """
        if not self.golden_cases_dir.exists():
            raise FileNotFoundError(
                f"Golden cases directory not found: {self.golden_cases_dir}"
            )
        
        golden_cases = []
        yaml_files = list(self.golden_cases_dir.glob("*.yaml")) + list(
            self.golden_cases_dir.glob("*.yml")
        )
        
        if not yaml_files:
            raise ValueError(
                f"No golden case YAML files found in {self.golden_cases_dir}"
            )
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)
                
                # Handle both single case and multiple cases in one file
                if isinstance(data, list):
                    for case_data in data:
                        golden_case = GoldenCase(**case_data)
                        if golden_case.status == "active":
                            golden_cases.append(golden_case)
                else:
                    golden_case = GoldenCase(**data)
                    if golden_case.status == "active":
                        golden_cases.append(golden_case)
            
            except Exception as e:
                raise ValueError(
                    f"Failed to load golden case from {yaml_file}: {e}"
                )
        
        return golden_cases
    
    def execute_case(self, golden_case: GoldenCase) -> CaseExecutionResult:
        """
        Execute a single golden case and validate the outcome.
        
        Args:
            golden_case: The golden case to execute
        
        Returns:
            CaseExecutionResult with validation results
        """
        start_time = time.time()
        
        try:
            # Create DecisionRequest from golden case input
            decision_request = self._create_decision_request(golden_case)
            
            # Execute the decision function
            decision_response = self.decision_function(decision_request)
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Validate the outcome
            validation_result = self._validate_outcome(
                golden_case.expected_outcome,
                decision_response,
            )
            
            return CaseExecutionResult(
                case_id=golden_case.case_id,
                case_version=golden_case.version,
                executed_at=datetime.utcnow(),
                execution_time_ms=execution_time_ms,
                success=True,
                decision_response=decision_response,
                outcome_matched=validation_result["outcome_matched"],
                boundary_violations_count=validation_result["boundary_violations"],
                governance_violations=validation_result["governance_violations"],
                assertion_failures=validation_result["assertion_failures"],
                confidence_score=getattr(decision_response, "confidence", None),
                human_review_required=getattr(
                    decision_response, "requires_human_review", False
                ),
            )
        
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            
            return CaseExecutionResult(
                case_id=golden_case.case_id,
                case_version=golden_case.version,
                executed_at=datetime.utcnow(),
                execution_time_ms=execution_time_ms,
                success=False,
                error=error_msg,
                outcome_matched=False,
            )
    
    def execute_all_cases(self) -> List[CaseExecutionResult]:
        """
        Execute all golden cases for this module.
        
        Returns:
            List of CaseExecutionResult objects
        """
        golden_cases = self.load_golden_cases()
        results = []
        
        for golden_case in golden_cases:
            result = self.execute_case(golden_case)
            results.append(result)
        
        return results
    
    def _create_decision_request(self, golden_case: GoldenCase) -> DecisionRequest:
        """
        Create a DecisionRequest from golden case input data.
        
        Args:
            golden_case: The golden case
        
        Returns:
            DecisionRequest object
        """
        # Extract required fields from input_data
        input_data = golden_case.input_data
        
        # Create DecisionRequest
        # Note: This is a simplified version. In production, you'd need to
        # properly map golden case input to DecisionRequest fields
        return DecisionRequest(
            request_id=f"eval_{golden_case.case_id}_{int(time.time())}",
            decision_type=golden_case.expected_outcome.decision_type,
            context=input_data,
            metadata={
                "evaluation_mode": True,
                "golden_case_id": golden_case.case_id,
                "golden_case_version": golden_case.version,
            },
        )
    
    def _validate_outcome(
        self,
        expected: ExpectedOutcome,
        actual: DecisionResponse,
    ) -> Dict[str, Any]:
        """
        Validate actual decision response against expected outcome.
        
        Args:
            expected: Expected outcome from golden case
            actual: Actual decision response
        
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "outcome_matched": True,
            "boundary_violations": 0,
            "governance_violations": [],
            "assertion_failures": [],
        }
        
        # Check decision type
        if hasattr(actual, "decision_type"):
            if actual.decision_type != expected.decision_type:
                validation_result["outcome_matched"] = False
                validation_result["assertion_failures"].append(
                    f"Decision type mismatch: expected {expected.decision_type}, "
                    f"got {actual.decision_type}"
                )
        
        # Check human review requirement
        if hasattr(actual, "requires_human_review"):
            if actual.requires_human_review != expected.requires_human_review:
                validation_result["outcome_matched"] = False
                validation_result["assertion_failures"].append(
                    f"Human review mismatch: expected {expected.requires_human_review}, "
                    f"got {actual.requires_human_review}"
                )
        
        # Check confidence bounds
        if hasattr(actual, "confidence") and actual.confidence is not None:
            if expected.min_confidence is not None:
                if actual.confidence < expected.min_confidence:
                    validation_result["outcome_matched"] = False
                    validation_result["assertion_failures"].append(
                        f"Confidence too low: {actual.confidence} < {expected.min_confidence}"
                    )
            
            if expected.max_confidence is not None:
                if actual.confidence > expected.max_confidence:
                    validation_result["outcome_matched"] = False
                    validation_result["assertion_failures"].append(
                        f"Confidence too high: {actual.confidence} > {expected.max_confidence}"
                    )
        
        # Check boundary violations
        if hasattr(actual, "boundary_violations"):
            violations_count = len(actual.boundary_violations)
            validation_result["boundary_violations"] = violations_count
            
            if expected.must_pass_boundaries and violations_count > 0:
                validation_result["outcome_matched"] = False
                validation_result["assertion_failures"].append(
                    f"Boundary violations not allowed: found {violations_count}"
                )
            elif violations_count > expected.boundary_violations_allowed:
                validation_result["outcome_matched"] = False
                validation_result["assertion_failures"].append(
                    f"Too many boundary violations: {violations_count} > "
                    f"{expected.boundary_violations_allowed}"
                )
        
        # Check governance requirements
        if expected.must_have_position:
            if not hasattr(actual, "position") or actual.position is None:
                validation_result["governance_violations"].append(
                    "Missing required position"
                )
                validation_result["outcome_matched"] = False
        
        if expected.must_have_explainability:
            if not hasattr(actual, "explainability") or actual.explainability is None:
                validation_result["governance_violations"].append(
                    "Missing required explainability"
                )
                validation_result["outcome_matched"] = False
            elif hasattr(actual.explainability, "factors"):
                factors_count = len(actual.explainability.factors)
                if factors_count < expected.min_explainability_factors:
                    validation_result["governance_violations"].append(
                        f"Insufficient explainability factors: {factors_count} < "
                        f"{expected.min_explainability_factors}"
                    )
                    validation_result["outcome_matched"] = False
        
        return validation_result


def create_runner(
    module_name: str,
    decision_function: Callable[[DecisionRequest], DecisionResponse],
    golden_cases_dir: Optional[Path] = None,
) -> EvaluationRunner:
    """
    Factory function to create an EvaluationRunner.
    
    Args:
        module_name: Name of the module being evaluated
        decision_function: Function that takes DecisionRequest and returns DecisionResponse
        golden_cases_dir: Optional directory containing golden case YAML files
    
    Returns:
        EvaluationRunner instance
    """
    return EvaluationRunner(
        module_name=module_name,
        decision_function=decision_function,
        golden_cases_dir=golden_cases_dir,
    )
