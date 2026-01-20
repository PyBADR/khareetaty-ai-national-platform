# Module Template

This template provides the exact structure for creating a new business module.

## Quick Start

```bash
# Create a new module
python tools/create_module.py --name my_module --description "My decision module"
```

## Manual Creation

If creating manually, copy this structure:

### Directory Structure

```
modules/my_module/
├── __init__.py
├── README.md
├── models.py
├── service.py
├── engine.py
├── config.py
├── tests/
│   ├── __init__.py
│   ├── test_service.py
│   ├── test_engine.py
│   └── test_models.py
└── examples/
    └── example_usage.py
```

### Template Files

Replace `MyModule` with your module name (PascalCase) and `my_module` with your module name (snake_case).

#### `__init__.py`

```python
"""
My Module - Business Decision Module

Brief description of what this module does.

Version: 1.0.0
"""

from .service import MyModuleService
from .models import MyModuleInput, MyModuleOutput

__all__ = [
    "MyModuleService",
    "MyModuleInput",
    "MyModuleOutput",
]
```

#### `models.py`

```python
"""
My Module Data Models

Input and output schemas for the module.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MyModuleInput(BaseModel):
    """
    Input schema for my_module.
    
    Define all required and optional input fields.
    """
    # TODO(my_module): Define input fields
    example_field: str = Field(..., description="Example required field")
    optional_field: Optional[int] = Field(None, description="Example optional field")
    
    class Config:
        json_schema_extra = {
            "example": {
                "example_field": "example_value",
                "optional_field": 42
            }
        }


class MyModuleOutput(BaseModel):
    """
    Output schema for my_module.
    
    Includes recommendation, confidence, and reasoning.
    """
    recommendation: Any = Field(..., description="Primary recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    reasoning: str = Field(..., description="Human-readable explanation")
    alternatives: List[Any] = Field(default_factory=list, description="Alternative recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": "approve",
                "confidence": 0.87,
                "reasoning": "All criteria met with high confidence",
                "alternatives": ["review", "reject"],
                "metadata": {"version": "1.0.0"}
            }
        }
```

#### `service.py`

```python
"""
My Module Service

Main entry point for my_module decisions.
"""

from typing import Optional
import logging

from core.decision_engine import (
    DecisionOrchestrator,
    DecisionType,
    DecisionContext,
    DecisionResult
)
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.telemetry import TelemetryCollector

from .models import MyModuleInput, MyModuleOutput
from .engine import MyModuleEngine
from .config import MyModuleConfig

logger = logging.getLogger(__name__)


class MyModuleService:
    """
    Service interface for my_module decisions.
    
    This is the main entry point that Spaces should use.
    """
    
    def __init__(
        self,
        config: Optional[MyModuleConfig] = None,
        orchestrator: Optional[DecisionOrchestrator] = None,
        policy_engine: Optional[PolicyEnforcer] = None,
        audit_logger: Optional[AuditLogger] = None,
        telemetry: Optional[TelemetryCollector] = None
    ):
        """
        Initialize the service.
        
        Args:
            config: Module configuration
            orchestrator: Decision orchestrator (optional)
            policy_engine: Policy enforcer (optional)
            audit_logger: Audit logger (optional)
            telemetry: Telemetry collector (optional)
        """
        self.config = config or MyModuleConfig()
        self.engine = MyModuleEngine(self.config)
        
        # Initialize core services
        self.orchestrator = orchestrator or DecisionOrchestrator(
            policy_engine=policy_engine,
            audit_logger=audit_logger,
            telemetry=telemetry
        )
    
    def execute(
        self,
        input_data: MyModuleInput,
        context: DecisionContext,
        decision_type: DecisionType = DecisionType.ADVISORY
    ) -> MyModuleOutput:
        """
        Execute a my_module decision.
        
        Args:
            input_data: Input parameters
            context: Decision context (user, trace_id, etc.)
            decision_type: Type of decision (ADVISORY, BOUNDED, SIMULATION)
            
        Returns:
            MyModuleOutput with recommendation and reasoning
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If decision execution fails
        """
        logger.info(
            f"Executing my_module decision",
            extra={"trace_id": context.trace_id}
        )
        
        # Step 1: Run business logic
        result = self.engine.process(input_data)
        
        # Step 2: Execute through orchestrator (handles policy, audit, telemetry)
        orchestrated_result = self.orchestrator.execute_decision(
            decision_type=decision_type,
            input_data=input_data.model_dump(),
            context=context,
            module_name="my_module"
        )
        
        # Step 3: Return module-specific output
        return result
```

#### `engine.py`

```python
"""
My Module Engine

Core business logic for my_module.
"""

import logging
from typing import Any, Dict, List

from .models import MyModuleInput, MyModuleOutput
from .config import MyModuleConfig

logger = logging.getLogger(__name__)


class MyModuleEngine:
    """
    Core business logic for my_module.
    
    This class contains the actual decision-making logic.
    """
    
    def __init__(self, config: MyModuleConfig):
        """
        Initialize the engine.
        
        Args:
            config: Module configuration
        """
        self.config = config
        
        # TODO(my_module): Initialize models, load weights, etc.
        logger.info("MyModuleEngine initialized")
    
    def process(self, input_data: MyModuleInput) -> MyModuleOutput:
        """
        Process input and generate recommendation.
        
        Args:
            input_data: Validated input data
            
        Returns:
            MyModuleOutput with recommendation
        """
        logger.info("Processing my_module request")
        
        # TODO(my_module): Implement actual business logic
        # Steps:
        # 1. Extract features from input
        # 2. Run model inference (if applicable)
        # 3. Apply business rules
        # 4. Generate explanation
        # 5. Calculate confidence
        # 6. Generate alternatives
        
        recommendation = self._generate_recommendation(input_data)
        confidence = self._calculate_confidence(input_data)
        reasoning = self._generate_reasoning(input_data, recommendation)
        alternatives = self._generate_alternatives(input_data, recommendation)
        
        return MyModuleOutput(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            metadata={
                "version": "1.0.0",
                "model": self.config.model_name
            }
        )
    
    def _generate_recommendation(self, input_data: MyModuleInput) -> Any:
        """
        Generate primary recommendation.
        
        TODO(my_module): Implement recommendation logic
        """
        return "placeholder_recommendation"
    
    def _calculate_confidence(self, input_data: MyModuleInput) -> float:
        """
        Calculate confidence score.
        
        TODO(my_module): Implement confidence calculation
        """
        return 0.85
    
    def _generate_reasoning(self, input_data: MyModuleInput, recommendation: Any) -> str:
        """
        Generate human-readable explanation.
        
        TODO(my_module): Implement explanation generation
        """
        return f"Recommendation '{recommendation}' based on input analysis"
    
    def _generate_alternatives(self, input_data: MyModuleInput, recommendation: Any) -> List[Any]:
        """
        Generate alternative recommendations.
        
        TODO(my_module): Implement alternatives generation
        """
        return []
```

#### `config.py`

```python
"""
My Module Configuration

Configuration settings for my_module.
"""

from typing import Optional
from pydantic import BaseModel, Field


class MyModuleConfig(BaseModel):
    """
    Configuration for my_module.
    
    All configuration should be externalized here.
    """
    # Model settings
    model_name: str = Field(
        default="default_model",
        description="Name of the model to use"
    )
    model_version: str = Field(
        default="1.0.0",
        description="Version of the model"
    )
    
    # Decision thresholds
    confidence_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for automated decisions"
    )
    
    # Performance settings
    max_processing_time_seconds: int = Field(
        default=30,
        ge=1,
        description="Maximum processing time in seconds"
    )
    
    # Feature flags
    enable_advanced_features: bool = Field(
        default=False,
        description="Enable advanced features"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "my_model_v2",
                "model_version": "2.0.0",
                "confidence_threshold": 0.90,
                "max_processing_time_seconds": 30,
                "enable_advanced_features": True
            }
        }
```

#### `README.md`

```markdown
# My Module

## Overview

Brief description of what this module does and what decisions it makes.

## Decision Type

- **Primary**: ADVISORY
- **Supported**: ADVISORY, BOUNDED, SIMULATION

## Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| example_field | string | Yes | Example required field |
| optional_field | integer | No | Example optional field |

## Output Schema

| Field | Type | Description |
|-------|------|-------------|
| recommendation | any | Primary recommendation |
| confidence | float | Confidence score (0.0-1.0) |
| reasoning | string | Human-readable explanation |
| alternatives | list | Alternative recommendations |
| metadata | dict | Additional metadata |

## Business Logic

Describe the decision-making logic:

1. Step 1: Extract features
2. Step 2: Apply rules
3. Step 3: Generate recommendation
4. Step 4: Calculate confidence
5. Step 5: Generate explanation

## Human-in-the-Loop

Human approval is required when:

- Confidence < 85%
- [Add other conditions]

## Usage Example

```python
from modules.my_module import MyModuleService, MyModuleInput
from core.decision_engine import DecisionContext, DecisionType

# Initialize service
service = MyModuleService()

# Create input
input_data = MyModuleInput(
    example_field="test_value",
    optional_field=42
)

# Create context
context = DecisionContext(
    user_id="user@example.com",
    user_role="analyst"
)

# Execute decision
result = service.execute(
    input_data=input_data,
    context=context,
    decision_type=DecisionType.ADVISORY
)

print(f"Recommendation: {result.recommendation}")
print(f"Confidence: {result.confidence}")
print(f"Reasoning: {result.reasoning}")
```

## Configuration

Configuration options:

- `model_name`: Name of the model to use
- `model_version`: Version of the model
- `confidence_threshold`: Minimum confidence for automated decisions
- `max_processing_time_seconds`: Maximum processing time
- `enable_advanced_features`: Enable advanced features

## Testing

```bash
# Run tests
pytest modules/my_module/tests/

# Run with coverage
pytest modules/my_module/tests/ --cov=modules.my_module
```

## Version History

- **v1.0.0** (2026-01-20) - Initial implementation
```

#### `tests/__init__.py`

```python
"""Tests for my_module."""
```

#### `tests/test_models.py`

```python
"""
Tests for my_module models.
"""

import pytest
from modules.my_module.models import MyModuleInput, MyModuleOutput


def test_input_validation():
    """Test input model validation."""
    # Valid input
    input_data = MyModuleInput(
        example_field="test",
        optional_field=42
    )
    assert input_data.example_field == "test"
    assert input_data.optional_field == 42


def test_output_validation():
    """Test output model validation."""
    # Valid output
    output = MyModuleOutput(
        recommendation="approve",
        confidence=0.87,
        reasoning="Test reasoning",
        alternatives=["review"],
        metadata={"test": "value"}
    )
    assert output.recommendation == "approve"
    assert output.confidence == 0.87
    assert 0.0 <= output.confidence <= 1.0
```

#### `tests/test_engine.py`

```python
"""
Tests for my_module engine.
"""

import pytest
from modules.my_module.engine import MyModuleEngine
from modules.my_module.models import MyModuleInput
from modules.my_module.config import MyModuleConfig


def test_engine_initialization():
    """Test engine initialization."""
    config = MyModuleConfig()
    engine = MyModuleEngine(config)
    assert engine.config == config


def test_engine_process():
    """Test engine processing."""
    config = MyModuleConfig()
    engine = MyModuleEngine(config)
    
    input_data = MyModuleInput(
        example_field="test"
    )
    
    result = engine.process(input_data)
    
    assert result.recommendation is not None
    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning != ""
```

#### `tests/test_service.py`

```python
"""
Tests for my_module service.
"""

import pytest
from modules.my_module.service import MyModuleService
from modules.my_module.models import MyModuleInput
from core.decision_engine import DecisionContext, DecisionType


def test_service_initialization():
    """Test service initialization."""
    service = MyModuleService()
    assert service.engine is not None
    assert service.orchestrator is not None


def test_service_execute():
    """Test service execution."""
    service = MyModuleService()
    
    input_data = MyModuleInput(
        example_field="test"
    )
    
    context = DecisionContext(
        user_id="test@example.com",
        user_role="analyst"
    )
    
    result = service.execute(
        input_data=input_data,
        context=context,
        decision_type=DecisionType.ADVISORY
    )
    
    assert result.recommendation is not None
    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning != ""
```

#### `examples/example_usage.py`

```python
"""
Example usage of my_module.
"""

from modules.my_module import MyModuleService, MyModuleInput
from core.decision_engine import DecisionContext, DecisionType


def main():
    """Run example."""
    # Initialize service
    service = MyModuleService()
    
    # Create input
    input_data = MyModuleInput(
        example_field="example_value",
        optional_field=42
    )
    
    # Create context
    context = DecisionContext(
        user_id="user@example.com",
        user_role="analyst"
    )
    
    # Execute decision
    result = service.execute(
        input_data=input_data,
        context=context,
        decision_type=DecisionType.ADVISORY
    )
    
    # Display results
    print("=" * 50)
    print("My Module Decision Result")
    print("=" * 50)
    print(f"Recommendation: {result.recommendation}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Alternatives: {result.alternatives}")
    print(f"Metadata: {result.metadata}")
    print("=" * 50)


if __name__ == "__main__":
    main()
```

## Checklist

When creating a new module from this template:

- [ ] Replace `MyModule` with your module name (PascalCase)
- [ ] Replace `my_module` with your module name (snake_case)
- [ ] Update all docstrings with actual descriptions
- [ ] Define input schema in `models.py`
- [ ] Define output schema in `models.py`
- [ ] Implement business logic in `engine.py`
- [ ] Configure settings in `config.py`
- [ ] Write comprehensive README
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add usage examples
- [ ] Remove all TODO markers after implementation
- [ ] Test locally before committing
