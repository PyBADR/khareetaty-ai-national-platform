# Telemetry Module

## Overview

The Telemetry module provides metrics collection, performance monitoring, and observability for all decision-making processes in the BDR Insurance Platform.

**Purpose**: Enable monitoring, alerting, and performance optimization

## Key Features

1. **Multiple Metric Types**: Counters, gauges, histograms, timers
2. **Decision Analytics**: Track risk scores, confidence, outcomes
3. **Performance Monitoring**: Measure execution times and throughput
4. **Compliance Tracking**: Monitor validation errors and violations
5. **Export Capabilities**: JSON and Prometheus formats
6. **Low Overhead**: Minimal performance impact

## Metric Types

### Counter
Monotonically increasing value. Use for:
- Total number of decisions
- Total errors
- Total overrides

### Gauge
Point-in-time value that can go up or down. Use for:
- Current queue depth
- Active sessions
- Memory usage

### Histogram
Distribution of values. Use for:
- Risk score distributions
- Confidence score distributions
- Claim amount distributions

### Timer
Duration measurements. Use for:
- Decision execution time
- API response time
- Database query time

## Usage Examples

### Example 1: Basic Metrics

```python
from core.telemetry import TelemetryCollector

telemetry = TelemetryCollector()

# Increment a counter
telemetry.increment_counter('decisions.total', tags={'type': 'fnol'})

# Set a gauge
telemetry.set_gauge('queue.depth', 42)

# Observe a histogram value
telemetry.observe_histogram('decisions.risk_score', 75.5)
```

### Example 2: Timing Operations

```python
# Using context manager
with telemetry.time_operation('decision.execute', tags={'type': 'fraud'}):
    # Code to time
    result = execute_decision(...)

# Manual timing
timer = telemetry.get_timer('policy.check')
timer.start()
# ... do work ...
metric = timer.stop()
print(f"Duration: {metric.value:.3f}s")
```

### Example 3: Decision Metrics

```python
# Record comprehensive decision metrics
telemetry.record_decision(
    decision_id='DEC-12345',
    decision_type='advisory',
    risk_score=65.5,
    confidence=0.87,
    duration_ms=125.3,
    outcome='approved',
    module='fnol_triage'
)
```

### Example 4: Validation and Compliance

```python
# Record validation errors
telemetry.record_validation_error(
    validation_type='input',
    error_type='missing_field',
    field='claim_id'
)

# Record compliance violations
telemetry.record_compliance_violation(
    rule_id='HUMAN_OVERSIGHT_001',
    severity='critical',
    decision_id='DEC-12345'
)
```

### Example 5: Human Overrides

```python
# Track when humans override system recommendations
telemetry.record_human_override(
    decision_type='fraud_detection',
    original='reject',
    override='approve',
    reason='additional_evidence'
)
```

### Example 6: Query Metrics

```python
from datetime import datetime, timedelta

# Get recent decision metrics
metrics = telemetry.get_metrics(
    name='decisions.total',
    start_time=datetime.now() - timedelta(hours=1),
    tags={'type': 'fnol'}
)

print(f"Found {len(metrics)} metrics")
```

### Example 7: Export Metrics

```python
# Export as JSON
json_export = telemetry.export_metrics(format='json')
with open('metrics.json', 'w') as f:
    f.write(json_export)

# Export in Prometheus format
prom_export = telemetry.export_metrics(format='prometheus')
print(prom_export)
```

### Example 8: Statistics

```python
stats = telemetry.get_statistics()

print(f"Total metrics: {stats['total_metrics']}")
print(f"By type: {stats['by_type']}")
print(f"By name: {stats['by_name']}")
print(f"Counters: {stats['counters']}")
print(f"Histograms: {stats['histograms']}")
```

## Integration with Decision Engine

```python
from core.decision_engine import DecisionOrchestrator
from core.telemetry import TelemetryCollector

telemetry = TelemetryCollector()

orchestrator = DecisionOrchestrator(
    policy_engine=policy_engine,
    audit_logger=audit_logger,
    telemetry=telemetry  # Inject telemetry
)

# Metrics are automatically collected during decision execution
result = orchestrator.execute_decision(...)
```

## Standard Metrics

### Decision Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `decisions.total` | Counter | Total number of decisions |
| `decisions.risk_score` | Histogram | Distribution of risk scores |
| `decisions.confidence` | Histogram | Distribution of confidence scores |
| `decisions.duration_ms` | Histogram | Decision execution time |
| `decisions.outcome.{outcome}` | Counter | Count by outcome (approved, rejected, etc.) |
| `decisions.overrides` | Counter | Human overrides of system recommendations |

### Validation Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `validation.errors` | Counter | Validation errors by type |
| `validation.warnings` | Counter | Validation warnings |

### Compliance Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `compliance.violations` | Counter | Compliance violations by rule |
| `compliance.checks` | Counter | Total compliance checks |

### Performance Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `decision.execute` | Timer | Decision execution time |
| `policy.check` | Timer | Policy check time |
| `audit.log` | Timer | Audit logging time |

## Tags

Tags provide dimensional data for metrics:

**Common Tags**:
- `decision_type`: Type of decision (advisory, bounded, simulation)
- `module`: Module name (fnol_triage, fraud_detection, etc.)
- `outcome`: Decision outcome (approved, rejected, escalated)
- `risk_level`: Risk level (low, medium, high)
- `user_id`: User identifier

**Example**:
```python
telemetry.increment_counter(
    'decisions.total',
    tags={
        'decision_type': 'advisory',
        'module': 'fnol_triage',
        'outcome': 'approved',
        'risk_level': 'low'
    }
)
```

## Monitoring & Alerting

### Key Metrics to Monitor

1. **Decision Volume**: `decisions.total`
   - Alert if drops to zero (system down)
   - Alert if spikes unexpectedly (potential issue)

2. **Error Rate**: `validation.errors`
   - Alert if error rate > 5%

3. **Compliance Violations**: `compliance.violations`
   - Alert on any critical violations

4. **Performance**: `decisions.duration_ms`
   - Alert if p95 > 1000ms
   - Alert if p99 > 5000ms

5. **Override Rate**: `decisions.overrides`
   - Monitor for unusual patterns
   - High override rate may indicate model issues

### Sample Alerts

```yaml
# Prometheus alert rules
groups:
  - name: bdr_insurance
    rules:
      - alert: HighErrorRate
        expr: rate(validation_errors[5m]) > 0.05
        annotations:
          summary: "High validation error rate"
      
      - alert: SlowDecisions
        expr: histogram_quantile(0.95, decisions_duration_ms) > 1000
        annotations:
          summary: "Decision execution time p95 > 1s"
      
      - alert: ComplianceViolation
        expr: increase(compliance_violations{severity="critical"}[5m]) > 0
        annotations:
          summary: "Critical compliance violation detected"
```

## Export Formats

### JSON Format

```json
[
  {
    "name": "decisions.total",
    "type": "counter",
    "value": 1523,
    "timestamp": "2026-01-20T10:30:00",
    "tags": {
      "decision_type": "advisory",
      "module": "fnol_triage"
    },
    "metadata": {}
  }
]
```

### Prometheus Format

```
# TYPE decisions_total counter
decisions_total{decision_type="advisory",module="fnol_triage"} 1523

# TYPE decisions_risk_score histogram
decisions_risk_score{decision_type="advisory"} 65.5
```

## Performance Considerations

1. **Low Overhead**: Metric collection adds < 1ms per operation
2. **Async Export**: Export metrics asynchronously to avoid blocking
3. **Sampling**: For high-volume scenarios, consider sampling
4. **Aggregation**: Aggregate metrics before export to reduce data volume
5. **Retention**: Define retention policies for historical metrics

## Best Practices

1. **Use Tags Wisely**: Don't create too many unique tag combinations (cardinality explosion)
2. **Consistent Naming**: Use dot notation (e.g., `decisions.total`)
3. **Document Metrics**: Maintain a metrics catalog
4. **Monitor Overhead**: Track telemetry system performance
5. **Test Alerts**: Regularly test alert rules

## Integration with Observability Tools

### Prometheus
```python
# Expose metrics endpoint
from flask import Flask, Response

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return Response(
        telemetry.export_metrics(format='prometheus'),
        mimetype='text/plain'
    )
```

### Grafana
Create dashboards using Prometheus data source:
- Decision volume over time
- Risk score distribution
- Performance percentiles
- Error rates

### DataDog / New Relic
Export metrics via their respective APIs or agents.

## TODO

- [ ] Add async metric export
- [ ] Implement metric sampling for high-volume scenarios
- [ ] Add support for metric aggregation
- [ ] Create Grafana dashboard templates
- [ ] Add integration with DataDog/New Relic
- [ ] Implement metric retention policies
- [ ] Add metric validation and schema enforcement

## Changelog

### v1.0.0 (2026-01-20)
- Initial implementation
- Support for Counter, Gauge, Histogram, Timer metrics
- Decision-specific metric recording
- JSON and Prometheus export formats
- Query and statistics capabilities
