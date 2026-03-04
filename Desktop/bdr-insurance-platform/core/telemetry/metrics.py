"""
Telemetry Metrics

Defines metric types and data structures for telemetry collection.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import time


class MetricType(str, Enum):
    """Type of metric"""
    COUNTER = "counter"  # Monotonically increasing value
    GAUGE = "gauge"  # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"  # Duration measurements


@dataclass
class Metric:
    """Base metric data structure"""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'name': self.name,
            'type': self.metric_type.value,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags,
            'metadata': self.metadata
        }


class Counter:
    """
    Counter metric - monotonically increasing value.
    
    Use for:
    - Total number of decisions
    - Total number of errors
    - Total number of overrides
    """
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.value = 0
    
    def increment(self, amount: float = 1.0) -> Metric:
        """Increment counter and return metric"""
        self.value += amount
        return Metric(
            name=self.name,
            metric_type=MetricType.COUNTER,
            value=self.value,
            timestamp=datetime.now(),
            tags=self.tags
        )
    
    def reset(self):
        """Reset counter to zero"""
        self.value = 0


class Gauge:
    """
    Gauge metric - point-in-time value that can go up or down.
    
    Use for:
    - Current queue depth
    - Active sessions
    - Memory usage
    """
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.value = 0.0
    
    def set(self, value: float) -> Metric:
        """Set gauge value and return metric"""
        self.value = value
        return Metric(
            name=self.name,
            metric_type=MetricType.GAUGE,
            value=self.value,
            timestamp=datetime.now(),
            tags=self.tags
        )
    
    def increment(self, amount: float = 1.0) -> Metric:
        """Increment gauge value"""
        self.value += amount
        return self.set(self.value)
    
    def decrement(self, amount: float = 1.0) -> Metric:
        """Decrement gauge value"""
        self.value -= amount
        return self.set(self.value)


class Histogram:
    """
    Histogram metric - distribution of values.
    
    Use for:
    - Risk score distributions
    - Confidence score distributions
    - Claim amount distributions
    """
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.values: List[float] = []
    
    def observe(self, value: float) -> Metric:
        """Observe a value and return metric"""
        self.values.append(value)
        
        # Calculate statistics
        if self.values:
            sorted_values = sorted(self.values)
            n = len(sorted_values)
            
            metadata = {
                'count': n,
                'sum': sum(sorted_values),
                'min': sorted_values[0],
                'max': sorted_values[-1],
                'mean': sum(sorted_values) / n,
                'p50': sorted_values[n // 2],
                'p95': sorted_values[int(n * 0.95)] if n > 1 else sorted_values[0],
                'p99': sorted_values[int(n * 0.99)] if n > 1 else sorted_values[0],
            }
        else:
            metadata = {}
        
        return Metric(
            name=self.name,
            metric_type=MetricType.HISTOGRAM,
            value=value,
            timestamp=datetime.now(),
            tags=self.tags,
            metadata=metadata
        )
    
    def reset(self):
        """Reset histogram"""
        self.values.clear()


class Timer:
    """
    Timer metric - measures duration of operations.
    
    Use for:
    - Decision execution time
    - API response time
    - Database query time
    
    Can be used as a context manager:
    
    with timer:
        # code to time
        pass
    """
    
    def __init__(self, name: str, tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.tags = tags or {}
        self.start_time: Optional[float] = None
        self.durations: List[float] = []
    
    def start(self):
        """Start the timer"""
        self.start_time = time.time()
    
    def stop(self) -> Metric:
        """Stop the timer and return metric"""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        
        duration = time.time() - self.start_time
        self.durations.append(duration)
        self.start_time = None
        
        # Calculate statistics
        if self.durations:
            sorted_durations = sorted(self.durations)
            n = len(sorted_durations)
            
            metadata = {
                'count': n,
                'sum': sum(sorted_durations),
                'min': sorted_durations[0],
                'max': sorted_durations[-1],
                'mean': sum(sorted_durations) / n,
                'p50': sorted_durations[n // 2],
                'p95': sorted_durations[int(n * 0.95)] if n > 1 else sorted_durations[0],
                'p99': sorted_durations[int(n * 0.99)] if n > 1 else sorted_durations[0],
            }
        else:
            metadata = {}
        
        return Metric(
            name=self.name,
            metric_type=MetricType.TIMER,
            value=duration,
            timestamp=datetime.now(),
            tags=self.tags,
            metadata=metadata
        )
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
        return False
    
    def reset(self):
        """Reset timer statistics"""
        self.durations.clear()
        self.start_time = None
