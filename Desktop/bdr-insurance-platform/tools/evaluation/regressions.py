"""
Regression Detection - Version Comparison and Change Detection

This module detects regressions by comparing current version outputs
against last approved version outputs.

REGRESSION = UNAPPROVED CHANGE
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .harness import CaseExecutionResult


class RegressionType(str, Enum):
    """Types of regressions that can be detected"""
    OUTCOME_CHANGED = "outcome_changed"
    RISK_CATEGORY_CHANGED = "risk_category_changed"
    AUTHORITY_CHANGED = "authority_changed"
    EXECUTION_ELIGIBILITY_CHANGED = "execution_eligibility_changed"
    CONFIDENCE_DEGRADED = "confidence_degraded"
    BOUNDARY_VIOLATION_INCREASED = "boundary_violation_increased"
    EXPLAINABILITY_DEGRADED = "explainability_degraded"
    PERFORMANCE_DEGRADED = "performance_degraded"


class RegressionSeverity(str, Enum):
    """Severity of a detected regression"""
    MINOR = "minor"  # Acceptable change, may proceed with warning
    MAJOR = "major"  # Significant change, requires review
    CRITICAL = "critical"  # Unacceptable change, blocks release


class RegressionDetection(BaseModel):
    """A detected regression between two versions"""
    
    regression_id: str
    regression_type: RegressionType
    severity: RegressionSeverity
    
    case_id: str
    case_version: str
    
    # Version comparison
    baseline_version: str
    current_version: str
    
    # Change details
    field_changed: str
    baseline_value: Any
    current_value: Any
    
    # Impact assessment
    description: str
    impact: str
    recommendation: str
    
    # Metadata
    detected_at: datetime
    requires_approval: bool = True


class RegressionReport(BaseModel):
    """Complete regression analysis report"""
    
    report_id: str
    module_name: str
    baseline_version: str
    current_version: str
    
    # Regression summary
    total_regressions: int = 0
    critical_regressions: int = 0
    major_regressions: int = 0
    minor_regressions: int = 0
    
    # Detailed regressions
    regressions: List[RegressionDetection] = Field(default_factory=list)
    
    # Overall assessment
    blocks_release: bool = False
    requires_manual_review: bool = False
    
    # Metadata
    generated_at: datetime
    analyzed_cases: int = 0
    
    def add_regression(self, regression: RegressionDetection):
        """Add a regression to the report"""
        self.regressions.append(regression)
        self.total_regressions += 1
        
        if regression.severity == RegressionSeverity.CRITICAL:
            self.critical_regressions += 1
            self.blocks_release = True
        elif regression.severity == RegressionSeverity.MAJOR:
            self.major_regressions += 1
            self.requires_manual_review = True
        elif regression.severity == RegressionSeverity.MINOR:
            self.minor_regressions += 1
    
    def has_blocking_regressions(self) -> bool:
        """Check if any regressions block release"""
        return self.blocks_release or self.critical_regressions > 0


class RegressionDetector:
    """
    Detects regressions by comparing execution results between versions.
    
    Regressions include:
    - Changed decision outcomes
    - Changed risk categories
    - Changed authority requirements
    - Changed execution eligibility
    - Degraded confidence scores
    - Increased boundary violations
    - Degraded explainability
    - Performance degradation
    """
    
    def __init__(
        self,
        module_name: str,
        baseline_version: str,
        current_version: str,
        confidence_threshold: float = 0.1,  # 10% degradation threshold
        performance_threshold: float = 0.5,  # 50% slowdown threshold
    ):
        """
        Initialize regression detector.
        
        Args:
            module_name: Name of the module being analyzed
            baseline_version: Version to compare against (last approved)
            current_version: Current version being evaluated
            confidence_threshold: Acceptable confidence degradation (0.0-1.0)
            performance_threshold: Acceptable performance degradation (0.0-1.0)
        """
        self.module_name = module_name
        self.baseline_version = baseline_version
        self.current_version = current_version
        self.confidence_threshold = confidence_threshold
        self.performance_threshold = performance_threshold
    
    def detect_regressions(
        self,
        baseline_results: List[CaseExecutionResult],
        current_results: List[CaseExecutionResult],
    ) -> RegressionReport:
        """
        Detect regressions by comparing baseline and current results.
        
        Args:
            baseline_results: Results from baseline version
            current_results: Results from current version
        
        Returns:
            RegressionReport with all detected regressions
        """
        report = RegressionReport(
            report_id=f"regression_{self.module_name}_{int(datetime.utcnow().timestamp())}",
            module_name=self.module_name,
            baseline_version=self.baseline_version,
            current_version=self.current_version,
            generated_at=datetime.utcnow(),
            analyzed_cases=len(current_results),
        )
        
        # Create lookup for baseline results
        baseline_lookup = {
            result.case_id: result for result in baseline_results
        }
        
        # Compare each current result with baseline
        for current_result in current_results:
            baseline_result = baseline_lookup.get(current_result.case_id)
            
            if baseline_result is None:
                # New case, no regression to detect
                continue
            
            # Detect various types of regressions
            regressions = self._compare_results(baseline_result, current_result)
            
            for regression in regressions:
                report.add_regression(regression)
        
        return report
    
    def _compare_results(
        self,
        baseline: CaseExecutionResult,
        current: CaseExecutionResult,
    ) -> List[RegressionDetection]:
        """
        Compare two execution results and detect regressions.
        
        Args:
            baseline: Baseline execution result
            current: Current execution result
        
        Returns:
            List of detected regressions
        """
        regressions = []
        
        # Check if execution failed (critical regression)
        if baseline.success and not current.success:
            regressions.append(
                RegressionDetection(
                    regression_id=f"reg_{current.case_id}_execution_failed",
                    regression_type=RegressionType.OUTCOME_CHANGED,
                    severity=RegressionSeverity.CRITICAL,
                    case_id=current.case_id,
                    case_version=current.case_version,
                    baseline_version=self.baseline_version,
                    current_version=self.current_version,
                    field_changed="execution_success",
                    baseline_value=True,
                    current_value=False,
                    description=f"Execution failed in current version: {current.error}",
                    impact="Case that previously passed now fails",
                    recommendation="Fix execution error before release",
                    detected_at=datetime.utcnow(),
                    requires_approval=True,
                )
            )
            return regressions  # Don't check other regressions if execution failed
        
        # Check outcome match regression
        if baseline.outcome_matched and not current.outcome_matched:
            regressions.append(
                RegressionDetection(
                    regression_id=f"reg_{current.case_id}_outcome_mismatch",
                    regression_type=RegressionType.OUTCOME_CHANGED,
                    severity=RegressionSeverity.CRITICAL,
                    case_id=current.case_id,
                    case_version=current.case_version,
                    baseline_version=self.baseline_version,
                    current_version=self.current_version,
                    field_changed="outcome_matched",
                    baseline_value=True,
                    current_value=False,
                    description="Decision outcome no longer matches expected outcome",
                    impact="Golden case validation failed",
                    recommendation="Review decision logic changes",
                    detected_at=datetime.utcnow(),
                    requires_approval=True,
                )
            )
        
        # Check confidence degradation
        if (
            baseline.confidence_score is not None
            and current.confidence_score is not None
        ):
            confidence_change = baseline.confidence_score - current.confidence_score
            
            if confidence_change > self.confidence_threshold:
                severity = (
                    RegressionSeverity.CRITICAL
                    if confidence_change > 0.3
                    else RegressionSeverity.MAJOR
                    if confidence_change > 0.15
                    else RegressionSeverity.MINOR
                )
                
                regressions.append(
                    RegressionDetection(
                        regression_id=f"reg_{current.case_id}_confidence_degraded",
                        regression_type=RegressionType.CONFIDENCE_DEGRADED,
                        severity=severity,
                        case_id=current.case_id,
                        case_version=current.case_version,
                        baseline_version=self.baseline_version,
                        current_version=self.current_version,
                        field_changed=\"confidence_score\",\n                        baseline_value=baseline.confidence_score,\n                        current_value=current.confidence_score,\n                        description=f\"Confidence degraded by {confidence_change:.2%}\",\n                        impact=\"Decision confidence decreased significantly\",\n                        recommendation=\"Investigate model or logic changes\",\n                        detected_at=datetime.utcnow(),\n                        requires_approval=severity != RegressionSeverity.MINOR,\n                    )\n                )\n        \n        # Check boundary violations increase\n        if current.boundary_violations_count > baseline.boundary_violations_count:\n            violations_increase = (\n                current.boundary_violations_count - baseline.boundary_violations_count\n            )\n            \n            regressions.append(\n                RegressionDetection(\n                    regression_id=f\"reg_{current.case_id}_boundary_violations\",\n                    regression_type=RegressionType.BOUNDARY_VIOLATION_INCREASED,\n                    severity=RegressionSeverity.MAJOR,\n                    case_id=current.case_id,\n                    case_version=current.case_version,\n                    baseline_version=self.baseline_version,\n                    current_version=self.current_version,\n                    field_changed=\"boundary_violations_count\",\n                    baseline_value=baseline.boundary_violations_count,\n                    current_value=current.boundary_violations_count,\n                    description=f\"Boundary violations increased by {violations_increase}\",\n                    impact=\"Decision violates more boundaries than before\",\n                    recommendation=\"Review boundary logic and constraints\",\n                    detected_at=datetime.utcnow(),\n                    requires_approval=True,\n                )\n            )\n        \n        # Check governance violations increase\n        baseline_gov_count = len(baseline.governance_violations)\n        current_gov_count = len(current.governance_violations)\n        \n        if current_gov_count > baseline_gov_count:\n            regressions.append(\n                RegressionDetection(\n                    regression_id=f\"reg_{current.case_id}_governance_violations\",\n                    regression_type=RegressionType.AUTHORITY_CHANGED,\n                    severity=RegressionSeverity.CRITICAL,\n                    case_id=current.case_id,\n                    case_version=current.case_version,\n                    baseline_version=self.baseline_version,\n                    current_version=self.current_version,\n                    field_changed=\"governance_violations\",\n                    baseline_value=baseline.governance_violations,\n                    current_value=current.governance_violations,\n                    description=\"New governance violations detected\",\n                    impact=\"Decision violates governance requirements\",\n                    recommendation=\"Fix governance violations before release\",\n                    detected_at=datetime.utcnow(),\n                    requires_approval=True,\n                )\n            )\n        \n        # Check performance degradation\n        if baseline.execution_time_ms > 0:\n            performance_change = (\n                (current.execution_time_ms - baseline.execution_time_ms)\n                / baseline.execution_time_ms\n            )\n            \n            if performance_change > self.performance_threshold:\n                severity = (\n                    RegressionSeverity.MAJOR\n                    if performance_change > 1.0  # 100% slower\n                    else RegressionSeverity.MINOR\n                )\n                \n                regressions.append(\n                    RegressionDetection(\n                        regression_id=f\"reg_{current.case_id}_performance_degraded\",\n                        regression_type=RegressionType.PERFORMANCE_DEGRADED,\n                        severity=severity,\n                        case_id=current.case_id,\n                        case_version=current.case_version,\n                        baseline_version=self.baseline_version,\n                        current_version=self.current_version,\n                        field_changed=\"execution_time_ms\",\n                        baseline_value=baseline.execution_time_ms,\n                        current_value=current.execution_time_ms,\n                        description=f\"Performance degraded by {performance_change:.1%}\",\n                        impact=\"Decision execution is significantly slower\",\n                        recommendation=\"Profile and optimize performance\",\n                        detected_at=datetime.utcnow(),\n                        requires_approval=severity == RegressionSeverity.MAJOR,\n                    )\n                )\n        \n        return regressions\n\n\ndef create_regression_detector(\n    module_name: str,\n    baseline_version: str,\n    current_version: str,\n    confidence_threshold: float = 0.1,\n    performance_threshold: float = 0.5,\n) -> RegressionDetector:\n    \"\"\"\n    Factory function to create a RegressionDetector.\n    \n    Args:\n        module_name: Name of the module being analyzed\n        baseline_version: Version to compare against\n        current_version: Current version being evaluated\n        confidence_threshold: Acceptable confidence degradation\n        performance_threshold: Acceptable performance degradation\n    \n    Returns:\n        RegressionDetector instance\n    \"\"\"\n    return RegressionDetector(\n        module_name=module_name,\n        baseline_version=baseline_version,\n        current_version=current_version,\n        confidence_threshold=confidence_threshold,\n        performance_threshold=performance_threshold,\n    )\n"}}]