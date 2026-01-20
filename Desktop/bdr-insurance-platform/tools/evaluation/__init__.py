"""
Evaluation Harness for BDR Insurance Platform

Provides formal evaluation infrastructure for decision modules.

Phase 3: Evaluation Harness as Release Gate
"""

from .harness import (
    EvaluationHarness,
    GoldenCase,
    CaseExecutionResult,
    ExpectedOutcome,
    run_evaluation,
)
from .metrics import (
    DecisionMetrics,
    StabilityMetrics,
    GovernanceMetrics,
    calculate_metrics,
)
from .runner import (
    EvaluationRunner,
    create_runner,
)
from .regressions import (
    RegressionType,
    RegressionSeverity,
    RegressionDetection,
    RegressionReport,
    RegressionDetector,
    create_regression_detector,
)
from .gates import (
    EvaluationResult,
    GateStatus,
    GateCheck,
    EvaluationGateResult,
    EvaluationGate,
    create_evaluation_gate,
)
from .report import (
    EvaluationReportGenerator,
    create_report_generator,
)

__all__ = [
    # Harness
    "EvaluationHarness",
    "GoldenCase",
    "CaseExecutionResult",
    "ExpectedOutcome",
    "run_evaluation",
    # Metrics
    "DecisionMetrics",
    "StabilityMetrics",
    "GovernanceMetrics",
    "calculate_metrics",
    # Runner
    "EvaluationRunner",
    "create_runner",
    # Regressions
    "RegressionType",
    "RegressionSeverity",
    "RegressionDetection",
    "RegressionReport",
    "RegressionDetector",
    "create_regression_detector",
    # Gates
    "EvaluationResult",
    "GateStatus",
    "GateCheck",
    "EvaluationGateResult",
    "EvaluationGate",
    "create_evaluation_gate",
    # Report
    "EvaluationReportGenerator",
    "create_report_generator",
]
