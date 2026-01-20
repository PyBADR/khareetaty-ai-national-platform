# Evaluation Harness

**NO METRICS = NO ENTERPRISE TRUST**

Formal evaluation infrastructure for the BDR Insurance Platform.

## Overview

The evaluation harness provides:

1. **Golden Case Management** - Immutable, versioned test cases
2. **Execution Engine** - Automated decision execution and validation
3. **Metrics Tracking** - Stability, drift, and governance metrics
4. **Regression Detection** - Automated comparison against baselines
5. **Reporting** - Comprehensive evaluation reports

## Architecture

```
tools/evaluation/
├── __init__.py              # Public API
├── harness.py               # Execution engine
├── metrics.py               # Metrics definitions
├── golden_cases/            # Test cases (YAML/JSON)
│   ├── fnol.yaml
│   ├── fraud.yaml
│   └── underwriting.yaml
├── reports/                 # Generated reports
│   └── README.md
└── README.md                # This file
```

## Quick Start

### Running Evaluation

```python
from tools.evaluation import run_evaluation
from modules.fnol_triage.service_contract import run_fnol_triage_contract

# Run evaluation for FNOL module
result = run_evaluation(
    module_name="fnol_triage",
    module_executor=run_fnol_triage_contract,
)

print(f"Pass Rate: {result.pass_rate:.1%}")
print(f"Governance Compliance: {result.governance_compliance_rate:.1%}")
print(f"Human Intervention Rate: {result.human_intervention_rate:.1%}")

# Check for failures
if result.failed_cases > 0:
    print(f"\n{result.failed_cases} cases failed:")
    for case_result in result.get_failed_cases():
        print(f"  - {case_result.case_id}: {case_result.assertion_failures}")
```

### Creating Golden Cases

Golden cases are defined in YAML or JSON format:

```yaml
- case_id: fnol_001
  version: 1.0.0
  module_name: fnol_triage
  title: High-value auto claim
  description: Tests handling of high-value claims
  category: normal
  difficulty: medium
  tags: [auto, high-value, human-review]
  
  input_data:
    claim_id: CLM-001
    claim_type: auto
    claim_amount: 75000.00
    description: "Total loss - vehicle collision"
  
  expected_outcome:
    decision_type: BOUNDED
    requires_human_review: true
    min_confidence: 0.7
    must_have_position: true
    must_have_explainability: true
  
  status: active
  created_at: "2026-01-20T10:00:00Z"
  created_by: platform_team
```

**Golden Case Rules:**

✅ **Immutable** - Never modify existing cases, create new versions
✅ **Versioned** - Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
✅ **Owned** - Each case has a creator and owner
✅ **Categorized** - normal, edge_case, adversarial
✅ **Difficulty-rated** - easy, medium, hard

### Expected Outcomes

Define what the decision should produce:

```python
expected_outcome = ExpectedOutcome(
    decision_type=DecisionTypeEnum.BOUNDED,
    requires_human_review=True,
    min_confidence=0.7,
    max_confidence=1.0,
    boundary_violations_allowed=1,
    must_pass_boundaries=False,
    must_have_position=True,
    must_have_explainability=True,
    min_explainability_factors=3,
    custom_assertions={
        "priority": "HIGH",
        "risk_category": "RED"
    }
)
```

## Metrics

### Decision Metrics

- **Accuracy** - Correctness (where ground truth available)
- **Precision/Recall** - Classification metrics
- **Confidence** - Average confidence scores
- **Execution Time** - Performance metrics (avg, p95, p99)

### Stability Metrics

- **Stability Score** - Consistency of decisions over time (0.0-1.0)
- **Decision Volatility** - Measure of decision changes
- **Flip Rate** - Rate of decision changes for same inputs
- **Drift Detection** - Systematic behavior changes

### Governance Metrics

- **Boundary Violation Rate** - % of decisions violating boundaries
- **Human Intervention Rate** - % requiring human review
- **Override Rate** - % of decisions overridden
- **Position Contract Compliance** - % with valid position contracts
- **Explainability Compliance** - % with complete explainability
- **Overall Governance Score** - Weighted average of all governance metrics

### Regression Detection

Compare current metrics to baseline:

```python
from tools.evaluation.metrics import detect_regression

regression = detect_regression(
    current_metrics=current_snapshot,
    baseline_metrics=baseline_snapshot,
)

if regression.has_critical_regression():
    print("CRITICAL REGRESSION DETECTED")
    print(regression.get_regression_summary())
    # Block deployment
```

**Regression Thresholds:**

- Accuracy drop > 5% = WARNING
- Accuracy drop > 10% = CRITICAL
- Governance score drop > 10% = CRITICAL
- Execution time increase > 50% = WARNING
- Boundary violation rate increase > 15% = CRITICAL

## Production Readiness

A module is production-ready when:

✅ Pass rate ≥ 95%
✅ Governance score ≥ 90%
✅ Stability score ≥ 80%
✅ No critical regressions

```python
if metrics_snapshot.is_production_ready():
    print(f"Module is production-ready (Grade: {metrics_snapshot.get_quality_grade()})")
else:
    print("Module NOT ready for production")
```

## CI/CD Integration

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

python tools/evaluation/run_quick_eval.py
if [ $? -ne 0 ]; then
    echo "Evaluation failed - commit blocked"
    exit 1
fi
```

### GitHub Actions

```yaml
name: Evaluation

on: [pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Evaluation
        run: |
          python -m tools.evaluation.run_all
      - name: Check Regressions
        run: |
          python -m tools.evaluation.check_regressions
      - name: Upload Reports
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-reports
          path: tools/evaluation/reports/
```

## Advanced Usage

### Custom Harness

```python
from pathlib import Path
from tools.evaluation import EvaluationHarness

harness = EvaluationHarness(
    golden_cases_dir=Path("custom/cases"),
    module_executor=my_custom_executor,
    module_name="my_module",
)

# Load cases
harness.load_golden_cases(pattern="*.yaml")

# Run evaluation
result = harness.run_evaluation()

# Save report
with open("my_report.json", "w") as f:
    f.write(result.model_dump_json(indent=2))
```

### Filtering Cases

```python
# Load only specific categories
harness.load_golden_cases(pattern="edge_case_*.yaml")

# Or filter after loading
harness.golden_cases = [
    case for case in harness.golden_cases
    if "high-value" in case.tags
]
```

### Custom Metrics

```python
from tools.evaluation.metrics import MetricsSnapshot

# TODO(metrics): Implement custom metric calculation
# This is a skeleton - real implementation needed
```

## Governance

### Case Ownership

- **Platform Team** - Core cases (fnol, fraud, underwriting)
- **Product Teams** - Product-specific cases
- **QA Team** - Edge cases and adversarial cases

### Review Process

1. **New Cases** - Require platform team approval
2. **Case Modifications** - Create new version, deprecate old
3. **Case Deletion** - Archive only, never delete
4. **Baseline Updates** - Monthly, after validation

### Audit Trail

All evaluations are logged:

- Evaluation ID
- Timestamp
- Module version
- Case versions
- Results
- Executor identity

## Troubleshooting

### Case Execution Failures

```python
for result in evaluation_result.case_results:
    if not result.success:
        print(f"Case {result.case_id} failed: {result.error}")
```

### Governance Violations

```python
violations = evaluation_result.get_governance_violations()
for violation in violations:
    print(f"Governance violation: {violation}")
```

### Low Pass Rate

1. Check failed cases: `result.get_failed_cases()`
2. Review assertion failures
3. Validate expected outcomes are correct
4. Check for module regressions

## Future Enhancements

- [ ] Implement metric calculation (currently skeleton)
- [ ] Add drift detection algorithms
- [ ] Create web dashboard for reports
- [ ] Add A/B testing support
- [ ] Implement custom assertion framework
- [ ] Add performance benchmarking
- [ ] Create case generation tools
- [ ] Add fuzzing support

## References

- [Golden Case Schema](./harness.py#GoldenCase)
- [Evaluation Result Schema](./harness.py#EvaluationResult)
- [Metrics Definitions](./metrics.py)
- [Report Formats](./reports/README.md)
