"""
Evaluation Harness - Formal Evaluation Infrastructure

This module provides the execution engine for running golden cases against
decision modules and capturing comprehensive evaluation results.

NO METRICS = NO ENTERPRISE TRUST
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
import yaml
import json

from core.decision_engine import (
    DecisionRequest,
    DecisionResponse,
    DecisionTypeEnum,
)


class GoldenCaseStatus(str, Enum):
    """Status of a golden case"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ExpectedOutcome(BaseModel):
    """Expected outcome for a golden case"""
    
    decision_type: DecisionTypeEnum
    requires_human_review: bool
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    expected_priority: Optional[str] = None
    expected_risk_level: Optional[str] = None
    expected_recommendation: Optional[str] = None
    boundary_violations_allowed: int = Field(0, ge=0)
    must_pass_boundaries: bool = True
    
    # Governance expectations
    must_have_position: bool = True
    must_have_explainability: bool = True
    min_explainability_factors: int = Field(1, ge=0)
    
    # Custom assertions (module-specific)
    custom_assertions: Dict[str, Any] = Field(default_factory=dict)


class GoldenCase(BaseModel):
    """
    A golden case is an immutable, versioned test case with:
    - Input data
    - Expected outcome
    - Metadata for tracking
    
    Golden cases are NEVER modified - create new versions instead.
    """
    
    case_id: str = Field(..., description="Unique identifier for this case")
    version: str = Field(..., description="Semantic version (e.g., 1.0.0)")
    module_name: str = Field(..., description="Target module (e.g., fnol_triage)")
    
    # Case metadata
    title: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="What this case tests")
    category: str = Field(..., description="Category (e.g., edge_case, normal, adversarial)")
    difficulty: str = Field(..., description="Difficulty (easy, medium, hard)")
    tags: List[str] = Field(default_factory=list)
    
    # Test data
    input_data: Dict[str, Any] = Field(..., description="Input to the decision module")
    expected_outcome: ExpectedOutcome
    
    # Governance
    status: GoldenCaseStatus = GoldenCaseStatus.ACTIVE
    created_at: datetime
    created_by: str
    last_validated: Optional[datetime] = None
    
    # Audit
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "fnol_001",
                "version": "1.0.0",
                "module_name": "fnol_triage",
                "title": "High-value auto claim",
                "description": "Tests handling of high-value claims requiring adjuster review",
                "category": "normal",
                "difficulty": "medium",
                "tags": ["auto", "high-value", "human-review"],
                "input_data": {
                    "claim_amount": 75000,
                    "claim_type": "auto",
                    "description": "Total loss - vehicle collision"
                },
                "expected_outcome": {
                    "decision_type": "BOUNDED",
                    "requires_human_review": True,
                    "min_confidence": 0.7,
                    "must_have_position": True,
                    "must_have_explainability": True
                },
                "status": "active",
                "created_at": "2026-01-20T10:00:00Z",
                "created_by": "platform_team"
            }
        }


class CaseExecutionResult(BaseModel):
    """Result of executing a single golden case"""
    
    case_id: str
    case_version: str
    executed_at: datetime
    execution_time_ms: float
    
    # Execution status
    success: bool
    error: Optional[str] = None
    
    # Decision output
    decision_response: Optional[DecisionResponse] = None
    
    # Validation results
    outcome_matched: bool = False
    boundary_violations_count: int = 0
    governance_violations: List[str] = Field(default_factory=list)
    assertion_failures: List[str] = Field(default_factory=list)
    
    # Metrics
    confidence_score: Optional[float] = None
    human_review_required: bool = False
    
    def is_passing(self) -> bool:
        """Check if this case passed all validations"""
        return (
            self.success
            and self.outcome_matched
            and len(self.assertion_failures) == 0
            and len(self.governance_violations) == 0
        )


class EvaluationResult(BaseModel):
    """Complete evaluation results for a module"""
    
    module_name: str
    evaluation_id: str
    executed_at: datetime
    total_execution_time_ms: float
    
    # Case results
    total_cases: int
    passed_cases: int
    failed_cases: int
    error_cases: int
    
    case_results: List[CaseExecutionResult]
    
    # Aggregate metrics
    pass_rate: float = Field(..., ge=0.0, le=1.0)
    avg_execution_time_ms: float
    avg_confidence: Optional[float] = None
    
    # Governance metrics
    boundary_violation_rate: float = Field(..., ge=0.0, le=1.0)
    human_intervention_rate: float = Field(..., ge=0.0, le=1.0)
    governance_compliance_rate: float = Field(..., ge=0.0, le=1.0)
    
    # Regression detection
    regression_detected: bool = False
    regression_notes: Optional[str] = None
    
    def get_failed_cases(self) -> List[CaseExecutionResult]:
        """Get all failed case results"""
        return [r for r in self.case_results if not r.is_passing()]
    
    def get_governance_violations(self) -> List[str]:
        """Get all unique governance violations"""
        violations = set()
        for result in self.case_results:
            violations.update(result.governance_violations)
        return sorted(list(violations))


class EvaluationHarness:
    """
    Formal evaluation harness for decision modules.
    
    Responsibilities:
    - Load golden cases from YAML/JSON
    - Execute module decisions
    - Validate outcomes against expectations
    - Capture comprehensive metrics
    - Detect regressions
    """
    
    def __init__(
        self,
        golden_cases_dir: Path,
        module_executor: Callable[[DecisionRequest], DecisionResponse],
        module_name: str,
    ):
        """
        Initialize the evaluation harness.
        
        Args:
            golden_cases_dir: Directory containing golden case files
            module_executor: Function that executes decisions (takes DecisionRequest, returns DecisionResponse)
            module_name: Name of the module being evaluated
        """
        self.golden_cases_dir = Path(golden_cases_dir)
        self.module_executor = module_executor
        self.module_name = module_name
        self.golden_cases: List[GoldenCase] = []
    
    def load_golden_cases(self, pattern: str = "*.yaml") -> int:
        """
        Load golden cases from files.
        
        Args:
            pattern: File pattern to match (default: *.yaml)
            
        Returns:
            Number of cases loaded
        """
        self.golden_cases = []
        
        for case_file in self.golden_cases_dir.glob(pattern):
            try:
                with open(case_file, 'r') as f:
                    if case_file.suffix in ['.yaml', '.yml']:
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                    
                    # Handle multiple cases in one file
                    if isinstance(data, list):
                        for case_data in data:
                            case = GoldenCase(**case_data)
                            if case.status == GoldenCaseStatus.ACTIVE:
                                self.golden_cases.append(case)
                    else:
                        case = GoldenCase(**data)
                        if case.status == GoldenCaseStatus.ACTIVE:
                            self.golden_cases.append(case)
                            
            except Exception as e:
                print(f"Warning: Failed to load {case_file}: {e}")
        
        return len(self.golden_cases)
    
    def execute_case(self, golden_case: GoldenCase) -> CaseExecutionResult:
        """
        Execute a single golden case.
        
        Args:
            golden_case: The case to execute
            
        Returns:
            Execution result with validation
        """
        start_time = datetime.now()
        
        result = CaseExecutionResult(
            case_id=golden_case.case_id,
            case_version=golden_case.version,
            executed_at=start_time,
            execution_time_ms=0.0,
            success=False,
        )
        
        try:
            # Create decision request
            request = DecisionRequest(
                decision_id=f"eval_{golden_case.case_id}_{start_time.isoformat()}",
                decision_type=golden_case.expected_outcome.decision_type,
                module_name=self.module_name,
                input_data=golden_case.input_data,
                user_id="evaluation_harness",
            )
            
            # Execute decision
            response = self.module_executor(request)
            result.decision_response = response
            result.success = True
            
            # Validate outcome
            result.outcome_matched = self._validate_outcome(golden_case, response)
            result.confidence_score = response.explainability.confidence_score if response.explainability else None
            result.human_review_required = response.human_review_required
            
            # Check governance
            result.governance_violations = self._check_governance(golden_case, response)
            
            # Count boundary violations
            if response.boundaries:
                result.boundary_violations_count = sum(
                    1 for check in response.boundaries.checks if not check.passed
                )
            
            # Custom assertions
            result.assertion_failures = self._check_assertions(golden_case, response)
            
        except Exception as e:
            result.success = False
            result.error = str(e)
        
        # Calculate execution time
        end_time = datetime.now()
        result.execution_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return result
    
    def _validate_outcome(self, golden_case: GoldenCase, response: DecisionResponse) -> bool:
        """Validate that the response matches expected outcome"""
        expected = golden_case.expected_outcome
        
        # Check human review requirement
        if expected.requires_human_review != response.human_review_required:
            return False
        
        # Check confidence bounds
        if response.explainability and response.explainability.confidence_score is not None:
            conf = response.explainability.confidence_score
            if expected.min_confidence is not None and conf < expected.min_confidence:
                return False
            if expected.max_confidence is not None and conf > expected.max_confidence:
                return False
        
        # Check boundary violations
        if response.boundaries:
            violation_count = sum(1 for check in response.boundaries.checks if not check.passed)
            if violation_count > expected.boundary_violations_allowed:
                return False
            if expected.must_pass_boundaries and violation_count > 0:
                return False
        
        return True
    
    def _check_governance(self, golden_case: GoldenCase, response: DecisionResponse) -> List[str]:
        """Check governance requirements"""
        violations = []
        expected = golden_case.expected_outcome
        
        # Check position contract
        if expected.must_have_position and not response.position:
            violations.append("Missing decision position contract")
        
        # Check explainability
        if expected.must_have_explainability and not response.explainability:
            violations.append("Missing explainability")
        elif response.explainability:
            factor_count = len(response.explainability.key_factors)
            if factor_count < expected.min_explainability_factors:
                violations.append(
                    f"Insufficient explainability factors: {factor_count} < {expected.min_explainability_factors}"
                )
        
        return violations
    
    def _check_assertions(self, golden_case: GoldenCase, response: DecisionResponse) -> List[str]:
        """Check custom assertions"""
        failures = []
        
        # TODO(evaluation): Implement custom assertion checking
        # This would allow module-specific validation logic
        
        return failures
    
    def run_evaluation(self) -> EvaluationResult:
        """
        Run evaluation on all loaded golden cases.
        
        Returns:
            Complete evaluation results
        """
        start_time = datetime.now()
        case_results = []
        
        for golden_case in self.golden_cases:
            result = self.execute_case(golden_case)
            case_results.append(result)
        
        end_time = datetime.now()
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Calculate aggregate metrics
        total_cases = len(case_results)
        passed_cases = sum(1 for r in case_results if r.is_passing())
        failed_cases = sum(1 for r in case_results if not r.is_passing() and r.success)
        error_cases = sum(1 for r in case_results if not r.success)
        
        pass_rate = passed_cases / total_cases if total_cases > 0 else 0.0
        avg_time = total_time_ms / total_cases if total_cases > 0 else 0.0
        
        # Calculate confidence average
        confidences = [r.confidence_score for r in case_results if r.confidence_score is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None
        
        # Calculate governance metrics
        boundary_violations = sum(r.boundary_violations_count for r in case_results)
        boundary_violation_rate = boundary_violations / total_cases if total_cases > 0 else 0.0
        
        human_interventions = sum(1 for r in case_results if r.human_review_required)
        human_intervention_rate = human_interventions / total_cases if total_cases > 0 else 0.0
        
        governance_compliant = sum(
            1 for r in case_results if len(r.governance_violations) == 0
        )
        governance_compliance_rate = governance_compliant / total_cases if total_cases > 0 else 0.0
        
        return EvaluationResult(
            module_name=self.module_name,
            evaluation_id=f"eval_{self.module_name}_{start_time.isoformat()}",
            executed_at=start_time,
            total_execution_time_ms=total_time_ms,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            error_cases=error_cases,
            case_results=case_results,
            pass_rate=pass_rate,
            avg_execution_time_ms=avg_time,
            avg_confidence=avg_confidence,
            boundary_violation_rate=boundary_violation_rate,
            human_intervention_rate=human_intervention_rate,
            governance_compliance_rate=governance_compliance_rate,
        )


def run_evaluation(
    module_name: str,
    module_executor: Callable[[DecisionRequest], DecisionResponse],
    golden_cases_dir: Optional[Path] = None,
) -> EvaluationResult:
    """
    Convenience function to run evaluation.
    
    Args:
        module_name: Name of the module to evaluate
        module_executor: Function that executes decisions
        golden_cases_dir: Directory with golden cases (default: tools/evaluation/golden_cases/{module_name})
        
    Returns:
        Evaluation results
    """
    if golden_cases_dir is None:
        golden_cases_dir = Path(__file__).parent / "golden_cases" / module_name
    
    harness = EvaluationHarness(
        golden_cases_dir=golden_cases_dir,
        module_executor=module_executor,
        module_name=module_name,
    )
    
    harness.load_golden_cases()
    return harness.run_evaluation()
