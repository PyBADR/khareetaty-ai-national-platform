"""
Telemetry Collector

Collects and aggregates metrics for monitoring and observability.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from .metrics import Metric, MetricType, Counter, Gauge, Histogram, Timer
import json


class TelemetryCollector:
    """
    Collects telemetry metrics for decision-making processes.
    
    Provides:
    - Metric collection and aggregation
    - Performance monitoring
    - Decision analytics
    - System health metrics
    """
    
    def __init__(self):
        self.metrics: List[Metric] = []
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.timers: Dict[str, Timer] = {}
    
    # Counter methods
    
    def get_counter(self, name: str, tags: Optional[Dict[str, str]] = None) -> Counter:
        """Get or create a counter"""
        key = self._make_key(name, tags)
        if key not in self.counters:
            self.counters[key] = Counter(name, tags)
        return self.counters[key]
    
    def increment_counter(self, name: str, amount: float = 1.0, 
                         tags: Optional[Dict[str, str]] = None) -> Metric:
        """Increment a counter and record metric"""
        counter = self.get_counter(name, tags)
        metric = counter.increment(amount)
        self.metrics.append(metric)
        return metric
    
    # Gauge methods
    
    def get_gauge(self, name: str, tags: Optional[Dict[str, str]] = None) -> Gauge:
        """Get or create a gauge"""
        key = self._make_key(name, tags)
        if key not in self.gauges:
            self.gauges[key] = Gauge(name, tags)
        return self.gauges[key]
    
    def set_gauge(self, name: str, value: float, 
                 tags: Optional[Dict[str, str]] = None) -> Metric:
        """Set a gauge value and record metric"""
        gauge = self.get_gauge(name, tags)
        metric = gauge.set(value)
        self.metrics.append(metric)
        return metric
    
    # Histogram methods
    
    def get_histogram(self, name: str, tags: Optional[Dict[str, str]] = None) -> Histogram:
        """Get or create a histogram"""
        key = self._make_key(name, tags)
        if key not in self.histograms:
            self.histograms[key] = Histogram(name, tags)
        return self.histograms[key]
    
    def observe_histogram(self, name: str, value: float, 
                         tags: Optional[Dict[str, str]] = None) -> Metric:
        """Observe a value in a histogram and record metric"""
        histogram = self.get_histogram(name, tags)
        metric = histogram.observe(value)
        self.metrics.append(metric)
        return metric
    
    # Timer methods
    
    def get_timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> Timer:
        """Get or create a timer"""
        key = self._make_key(name, tags)
        if key not in self.timers:
            self.timers[key] = Timer(name, tags)
        return self.timers[key]
    
    def time_operation(self, name: str, tags: Optional[Dict[str, str]] = None) -> Timer:
        """
        Get a timer for use as a context manager.
        
        Usage:
            with telemetry.time_operation('decision.execute'):
                # code to time
                pass
        """
        return self.get_timer(name, tags)
    
    # Decision-specific metrics
    
    def record_decision(self,
                       decision_id: str,
                       decision_type: str,
                       risk_score: float,
                       confidence: float,
                       duration_ms: float,
                       outcome: str,
                       **tags):
        """
        Record comprehensive decision metrics.
        
        Args:
            decision_id: Unique decision identifier
            decision_type: Type of decision (advisory, bounded, simulation)
            risk_score: Risk score (0-100)
            confidence: Model confidence (0-1)
            duration_ms: Decision execution time in milliseconds
            outcome: Decision outcome (approved, rejected, escalated, etc.)
            **tags: Additional tags
        """
        base_tags = {
            'decision_type': decision_type,
            'outcome': outcome,
            **tags
        }
        
        # Count total decisions
        self.increment_counter('decisions.total', tags=base_tags)
        
        # Record risk score distribution
        self.observe_histogram('decisions.risk_score', risk_score, tags=base_tags)
        
        # Record confidence distribution
        self.observe_histogram('decisions.confidence', confidence, tags=base_tags)
        
        # Record execution time
        self.observe_histogram('decisions.duration_ms', duration_ms, tags=base_tags)
        
        # Count by outcome
        outcome_tags = {'outcome': outcome}
        self.increment_counter(f'decisions.outcome.{outcome}', tags=outcome_tags)
    
    def record_validation_error(self, validation_type: str, error_type: str, **tags):
        """Record validation errors"""
        error_tags = {
            'validation_type': validation_type,
            'error_type': error_type,
            **tags
        }
        self.increment_counter('validation.errors', tags=error_tags)
    
    def record_compliance_violation(self, rule_id: str, severity: str, **tags):
        """Record compliance violations"""
        violation_tags = {
            'rule_id': rule_id,
            'severity': severity,
            **tags
        }
        self.increment_counter('compliance.violations', tags=violation_tags)
    
    def record_human_override(self, decision_type: str, original: str, override: str, **tags):
        """Record human overrides of system recommendations"""
        override_tags = {
            'decision_type': decision_type,
            'original': original,
            'override': override,
            **tags
        }
        self.increment_counter('decisions.overrides', tags=override_tags)
    
    # Query and export methods
    
    def get_metrics(self,
                   name: Optional[str] = None,
                   metric_type: Optional[MetricType] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   tags: Optional[Dict[str, str]] = None,
                   limit: Optional[int] = None) -> List[Metric]:
        """
        Query metrics with filters.
        
        Args:
            name: Filter by metric name
            metric_type: Filter by metric type
            start_time: Filter metrics after this time
            end_time: Filter metrics before this time
            tags: Filter by tags (all must match)
            limit: Maximum number of metrics to return
        
        Returns:
            List of matching metrics
        """
        results = self.metrics
        
        # Apply filters
        if name:
            results = [m for m in results if m.name == name]
        
        if metric_type:
            results = [m for m in results if m.metric_type == metric_type]
        
        if start_time:
            results = [m for m in results if m.timestamp >= start_time]
        
        if end_time:
            results = [m for m in results if m.timestamp <= end_time]
        
        if tags:
            results = [
                m for m in results 
                if all(m.tags.get(k) == v for k, v in tags.items())
            ]
        
        # Sort by timestamp (newest first)
        results = sorted(results, key=lambda m: m.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get telemetry statistics.
        
        Returns:
            Dictionary with statistics
        """
        if not self.metrics:
            return {
                'total_metrics': 0,
                'by_type': {},
                'by_name': {},
                'oldest_metric': None,
                'newest_metric': None
            }
        
        by_type = {}
        by_name = {}
        
        for metric in self.metrics:
            # Count by type
            type_str = metric.metric_type.value
            by_type[type_str] = by_type.get(type_str, 0) + 1
            
            # Count by name
            by_name[metric.name] = by_name.get(metric.name, 0) + 1
        
        sorted_metrics = sorted(self.metrics, key=lambda m: m.timestamp)
        
        return {
            'total_metrics': len(self.metrics),
            'by_type': by_type,
            'by_name': by_name,
            'counters': len(self.counters),
            'gauges': len(self.gauges),
            'histograms': len(self.histograms),
            'timers': len(self.timers),
            'oldest_metric': sorted_metrics[0].timestamp.isoformat(),
            'newest_metric': sorted_metrics[-1].timestamp.isoformat()
        }
    
    def export_metrics(self, format: str = 'json') -> str:
        """
        Export metrics in specified format.
        
        Args:
            format: Export format ('json' or 'prometheus')
        
        Returns:
            Exported metrics as string
        """
        if format == 'json':
            return json.dumps([m.to_dict() for m in self.metrics], indent=2)
        elif format == 'prometheus':
            return self._export_prometheus()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics
        """
        lines = []
        
        # Group metrics by name
        by_name: Dict[str, List[Metric]] = {}
        for metric in self.metrics:
            if metric.name not in by_name:
                by_name[metric.name] = []
            by_name[metric.name].append(metric)
        
        # Format each metric group
        for name, metrics in by_name.items():
            if not metrics:
                continue
            
            metric_type = metrics[0].metric_type
            
            # Add type comment
            if metric_type == MetricType.COUNTER:
                lines.append(f"# TYPE {name} counter")
            elif metric_type == MetricType.GAUGE:
                lines.append(f"# TYPE {name} gauge")
            elif metric_type in (MetricType.HISTOGRAM, MetricType.TIMER):
                lines.append(f"# TYPE {name} histogram")
            
            # Add metric values
            for metric in metrics:
                tags_str = ','.join([f'{k}="{v}"' for k, v in metric.tags.items()])
                if tags_str:
                    lines.append(f"{name}{{{tags_str}}} {metric.value}")
                else:
                    lines.append(f"{name} {metric.value}")
        
        return '\n'.join(lines)
    
    def clear(self):
        """Clear all metrics and reset collectors"""
        self.metrics.clear()
        self.counters.clear()
        self.gauges.clear()
        self.histograms.clear()
        self.timers.clear()
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Create a unique key for a metric"""
        if not tags:
            return name
        tags_str = ','.join(sorted([f"{k}={v}" for k, v in tags.items()]))
        return f"{name}[{tags_str}]"
