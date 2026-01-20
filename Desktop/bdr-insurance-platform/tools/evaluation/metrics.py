"""
Evaluation Metrics - Stability, Drift, and Governance Tracking

NO METRICS = NO ENTERPRISE TRUST

This module defines metrics for:
- Decision stability (consistency over time)
- Decision drift (changes in behavior)
- Governance violations
- Regression detection
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MetricSeverity(str, Enum):
    """Severity level for metric violations"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DecisionMetrics(BaseModel):
    """
    Core decision quality metrics.
    
    These metrics measure the quality and consistency of decisions.
    """
    
    # Accuracy metrics (where ground truth is available)
    accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall accuracy")
    precision: Optional[float] = Field(None, ge=0.0, le=1.0, description="Precision")
    recall: Optional[float] = Field(None, ge=0.0, le=1.0, description="Recall")
    f1_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="F1 score")
    
    # Confidence metrics
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    confidence_std_dev: float = Field(..., ge=0.0, description="Confidence standard deviation")
    low_confidence_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of low confidence decisions")
    
    # Decision distribution
    decision_count: int = Field(..., ge=0)
    unique_outcomes: int = Field(..., ge=0)
    outcome_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Performance
    avg_execution_time_ms: float = Field(..., ge=0.0)
    p95_execution_time_ms: float = Field(..., ge=0.0)
    p99_execution_time_ms: float = Field(..., ge=0.0)


class StabilityMetrics(BaseModel):
    """
    Decision stability and drift metrics.
    
    Stability = consistency of decisions for similar inputs over time.
    Drift = systematic changes in decision behavior.
    """
    
    # Stability metrics
    stability_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Overall stability (1.0 = perfectly stable)"
    )
    
    decision_volatility: float = Field(
        ...,
        ge=0.0,
        description="Measure of decision changes (lower is better)"
    )
    
    flip_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Rate of decision changes for same inputs"
    )
    
    # Drift detection
    drift_detected: bool = Field(..., description="Whether drift was detected")
    drift_magnitude: Optional[float] = Field(None, ge=0.0, description="Magnitude of drift")
    drift_direction: Optional[str] = Field(None, description="Direction of drift")
    
    # Temporal analysis
    time_window_start: datetime
    time_window_end: datetime
    baseline_period: Optional[str] = None
    
    # Confidence drift
    confidence_drift: float = Field(
        ...,
        description="Change in average confidence over time"
    )
    
    # Boundary violation drift
    boundary_violation_drift: float = Field(
        ...,
        description="Change in boundary violation rate"
    )


class GovernanceMetrics(BaseModel):
    """
    Governance and compliance metrics.
    
    These metrics track adherence to governance policies and regulatory requirements.
    """
    
    # Boundary compliance
    boundary_violation_rate: float = Field(..., ge=0.0, le=1.0)
    boundary_violations_by_type: Dict[str, int] = Field(default_factory=dict)
    critical_boundary_violations: int = Field(..., ge=0)
    
    # Human-in-the-loop metrics
    human_intervention_rate: float = Field(..., ge=0.0, le=1.0)
    override_rate: float = Field(..., ge=0.0, le=1.0)
    escalation_rate: float = Field(..., ge=0.0, le=1.0)
    avg_review_time_hours: Optional[float] = Field(None, ge=0.0)
    
    # Position contract compliance
    position_contract_compliance: float = Field(..., ge=0.0, le=1.0)
    missing_position_count: int = Field(..., ge=0)
    
    # Explainability compliance
    explainability_compliance: float = Field(..., ge=0.0, le=1.0)
    missing_explainability_count: int = Field(..., ge=0)
    avg_explainability_factors: float = Field(..., ge=0.0)
    
    # Lifecycle compliance
    lifecycle_compliance: float = Field(..., ge=0.0, le=1.0)
    invalid_state_transitions: int = Field(..., ge=0)
    blocked_decisions: int = Field(..., ge=0)
    
    # Audit trail
    audit_metadata_compliance: float = Field(..., ge=0.0, le=1.0)
    missing_audit_metadata_count: int = Field(..., ge=0)
    
    # Overall governance score
    overall_governance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weighted average of all governance metrics"
    )


class RegressionMetrics(BaseModel):
    """
    Regression detection metrics.
    
    Compares current performance against baseline to detect regressions.
    """
    
    regression_detected: bool
    severity: MetricSeverity
    
    # Performance regressions
    accuracy_delta: Optional[float] = None
    confidence_delta: float
    execution_time_delta: float
    
    # Governance regressions
    boundary_violation_delta: float
    human_intervention_delta: float
    governance_score_delta: float
    
    # Specific regressions
    regressions: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    
    # Baseline info
    baseline_id: str
    baseline_date: datetime
    current_date: datetime
    
    def has_critical_regression(self) -> bool:
        """Check if any critical regressions were detected"""
        return self.regression_detected and self.severity == MetricSeverity.CRITICAL
    
    def get_regression_summary(self) -> str:
        """Get human-readable regression summary"""
        if not self.regression_detected:
            return "No regressions detected"
        
        summary = f"Regression detected ({self.severity.value}):\n"
        for regression in self.regressions:
            summary += f"  - {regression}\n"
        
        if self.improvements:
            summary += "Improvements:\n"
            for improvement in self.improvements:
                summary += f"  + {improvement}\n"
        
        return summary


class MetricsSnapshot(BaseModel):
    """
    Complete metrics snapshot for a module at a point in time.
    
    This is the primary artifact for tracking module performance over time.
    """
    
    snapshot_id: str
    module_name: str
    snapshot_date: datetime
    
    # Core metrics
    decision_metrics: DecisionMetrics
    stability_metrics: StabilityMetrics
    governance_metrics: GovernanceMetrics
    
    # Regression (if baseline available)
    regression_metrics: Optional[RegressionMetrics] = None
    
    # Metadata
    evaluation_id: str
    total_cases_evaluated: int
    pass_rate: float = Field(..., ge=0.0, le=1.0)
    
    # Notes
    notes: Optional[str] = None
    
    def is_production_ready(self) -> bool:
        """
        Determine if module is production-ready based on metrics.
        
        Criteria:
        - Pass rate >= 95%
        - Governance score >= 90%
        - No critical regressions
        - Stability score >= 80%
        """
        criteria = [
            self.pass_rate >= 0.95,
            self.governance_metrics.overall_governance_score >= 0.90,
            self.stability_metrics.stability_score >= 0.80,
        ]
        
        if self.regression_metrics:
            criteria.append(not self.regression_metrics.has_critical_regression())
        
        return all(criteria)
    
    def get_quality_grade(self) -> str:
        """Get overall quality grade (A-F)"""
        score = (
            self.pass_rate * 0.4 +
            self.governance_metrics.overall_governance_score * 0.3 +
            self.stability_metrics.stability_score * 0.3
        )
        
        if score >= 0.95:
            return "A"
        elif score >= 0.90:
            return "B"
        elif score >= 0.80:
            return "C"
        elif score >= 0.70:
            return "D"
        else:
            return "F"


def calculate_metrics(
    evaluation_results: List[Dict],
    baseline_metrics: Optional[MetricsSnapshot] = None,
) -> MetricsSnapshot:
    """
    Calculate comprehensive metrics from evaluation results.
    
    Args:
        evaluation_results: List of evaluation result dictionaries
        baseline_metrics: Optional baseline for regression detection
        
    Returns:
        Complete metrics snapshot
        
    TODO(metrics): Implement actual metric calculations
    This is a skeleton - real implementation would:
    1. Parse evaluation results
    2. Calculate decision metrics (accuracy, confidence, etc.)
    3. Calculate stability metrics (volatility, drift)
    4. Calculate governance metrics (compliance rates)
    5. Detect regressions against baseline
    6. Generate snapshot
    """
    raise NotImplementedError(
        "Metric calculation not yet implemented. "
        "This requires actual evaluation data and statistical analysis."
    )


def detect_regression(
    current_metrics: MetricsSnapshot,
    baseline_metrics: MetricsSnapshot,
    thresholds: Optional[Dict[str, float]] = None,
) -> RegressionMetrics:
    """
    Detect regressions by comparing current metrics to baseline.
    
    Args:
        current_metrics: Current metrics snapshot
        baseline_metrics: Baseline metrics snapshot
        thresholds: Optional custom thresholds for regression detection
        
    Returns:
        Regression metrics with detected issues
        
    TODO(metrics): Implement regression detection logic
    Default thresholds:
    - Accuracy drop > 5% = WARNING
    - Accuracy drop > 10% = CRITICAL
    - Governance score drop > 10% = CRITICAL
    - Execution time increase > 50% = WARNING
    """
    raise NotImplementedError(
        "Regression detection not yet implemented. "
        "This requires statistical comparison and threshold configuration."
    )


def calculate_stability_score(
    decision_history: List[Dict],
    time_window: timedelta = timedelta(days=30),
) -> float:
    """
    Calculate stability score based on decision history.
    
    Stability = consistency of decisions for similar inputs over time.
    
    Args:
        decision_history: Historical decision data
        time_window: Time window for analysis
        
    Returns:
        Stability score (0.0 to 1.0, higher is better)
        
    TODO(metrics): Implement stability calculation
    Algorithm:
    1. Group similar inputs (using similarity threshold)
    2. Calculate decision consistency within groups
    3. Weight by recency (recent decisions matter more)
    4. Aggregate into overall score
    """
    raise NotImplementedError(
        "Stability calculation not yet implemented. "
        "This requires decision history and similarity metrics."
    )


def detect_drift(
    current_period_decisions: List[Dict],
    baseline_period_decisions: List[Dict],
) -> Dict[str, any]:
    """
    Detect drift in decision behavior.
    
    Drift = systematic changes in decision patterns over time.
    
    Args:
        current_period_decisions: Recent decisions
        baseline_period_decisions: Baseline period decisions
        
    Returns:
        Drift detection results with magnitude and direction
        
    TODO(metrics): Implement drift detection
    Methods:
    1. Statistical tests (KS test, chi-square)
    2. Distribution comparison
    3. Confidence interval analysis
    4. Boundary violation rate changes
    """
    raise NotImplementedError(
        "Drift detection not yet implemented. "
        "This requires statistical analysis of decision distributions."
    )
