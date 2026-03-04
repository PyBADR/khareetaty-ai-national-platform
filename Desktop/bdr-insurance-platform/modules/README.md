# Business Modules

## Overview

The `modules/` directory contains **business decision products**. Each module represents a distinct insurance decision capability:

- **fnol_triage** - First Notice of Loss triage and prioritization
- **fraud_detection** - Claims fraud detection and risk scoring
- **ifrs_accrual** - IFRS 17 accrual estimation
- **underwriting_scoring** - Risk assessment and pricing
- **reinsurance_pricing** - Reinsurance treaty pricing

## Architecture Principles

### 1. **Modules are Products**
Each module is a self-contained product with:
- Clear input/output contracts
- Defined decision type (ADVISORY, BOUNDED, SIMULATION)
- Human-in-the-loop hooks
- Complete documentation

### 2. **Modules Use Core Services**
All modules MUST use core platform services:
- Decision orchestration via `core.decision_engine`
- Policy enforcement via `core.policy_engine`
- Audit logging via `core.audit_logging`
- Security via `core.security`

### 3. **Modules Never Bypass Core**
Modules MUST NOT:
- Implement their own decision orchestration
- Implement their own audit logging
- Implement their own policy enforcement
- Bypass security checks

### 4. **Modules are Isolated**
Modules MUST NOT:
- Import from other modules
- Share state with other modules
- Depend on execution order

## Standard Module Structure

Every module MUST follow this structure:

```
modules/<module_name>/
├── __init__.py              # Public API exports
├── README.md                # Module documentation
├── models.py                # Input/output schemas (Pydantic)
├── service.py               # Main service interface
├── engine.py                # Business logic implementation
├── config.py                # Module configuration
├── tests/                   # Unit and integration tests
│   ├── __init__.py
│   ├── test_service.py
│   ├── test_engine.py
│   └── test_models.py
└── examples/                # Usage examples
    └── example_usage.py
```

### File Responsibilities

#### `__init__.py`
Defines the public API. Only exports what Spaces should use.

```python
"""
<Module Name> - Business Decision Module

Brief description of what this module does.
"""

from .service import <ModuleName>Service
from .models import <ModuleName>Input, <ModuleName>Output

__all__ = [
    "<ModuleName>Service",
    "<ModuleName>Input",
    "<ModuleName>Output",
]
```

#### `models.py`
Defines input/output schemas using Pydantic.

```python
"""
<Module Name> Data Models

Input and output schemas for the module.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class <ModuleName>Input(BaseModel):
    """
    Input schema for <module_name>.
    
    All required fields must be documented.
    """
    # Define input fields
    field1: str = Field(..., description="Description of field1")
    field2: int = Field(..., ge=0, description="Description of field2")
    optional_field: Optional[str] = Field(None, description="Optional field")
    
    class Config:
        json_schema_extra = {
            "example": {
                "field1": "example_value",
                "field2": 42,
                "optional_field": "optional_value"
            }
        }


class <ModuleName>Output(BaseModel):
    """
    Output schema for <module_name>.
    
    Includes recommendation, confidence, and reasoning.
    """
    recommendation: Any = Field(..., description="Primary recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(..., description="Explanation of recommendation")
    alternatives: List[Any] = Field(default_factory=list, description="Alternative recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendation": "high_priority",
                "confidence": 0.87,
                "reasoning": "High severity with fraud indicators",
                "alternatives": ["medium_priority"],
                "metadata": {"severity_score": 8.5}
            }
        }
```

#### `service.py`
Main service interface that Spaces call. Integrates with core services.

```python
"""
<Module Name> Service

Main entry point for <module_name> decisions.
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

from .models import <ModuleName>Input, <ModuleName>Output
from .engine import <ModuleName>Engine
from .config import <ModuleName>Config

logger = logging.getLogger(__name__)


class <ModuleName>Service:
    """
    Service interface for <module_name> decisions.
    
    This is the main entry point that Spaces should use.
    """
    
    def __init__(
        self,
        config: Optional[<ModuleName>Config] = None,
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
        self.config = config or <ModuleName>Config()
        self.engine = <ModuleName>Engine(self.config)
        
        # Initialize core services
        self.orchestrator = orchestrator or DecisionOrchestrator(
            policy_engine=policy_engine,
            audit_logger=audit_logger,
            telemetry=telemetry
        )
    
    def execute(
        self,
        input_data: <ModuleName>Input,
        context: DecisionContext,
        decision_type: DecisionType = DecisionType.ADVISORY
    ) -> <ModuleName>Output:
        """
        Execute a <module_name> decision.
        
        Args:
            input_data: Input parameters
            context: Decision context (user, trace_id, etc.)
            decision_type: Type of decision (ADVISORY, BOUNDED, SIMULATION)
            
        Returns:
            <ModuleName>Output with recommendation and reasoning
            
        Raises:
            ValueError: If input validation fails
            RuntimeError: If decision execution fails
        """
        logger.info(
            f"Executing <module_name> decision",
            extra={"trace_id": context.trace_id}
        )
        
        # Step 1: Run business logic
        result = self.engine.process(input_data)
        
        # Step 2: Convert to DecisionResult format
        decision_result = DecisionResult(
            decision_type=decision_type,
            recommendation=result.recommendation,
            confidence=result.confidence,
            reasoning=result.reasoning,
            alternatives=result.alternatives,
            metadata=result.metadata
        )
        
        # Step 3: Execute through orchestrator (handles policy, audit, telemetry)
        orchestrated_result = self.orchestrator.execute_decision(
            decision_type=decision_type,
            input_data=input_data.model_dump(),
            context=context,
            module_name="<module_name>"
        )
        
        # Step 4: Return module-specific output
        return result
```

#### `engine.py`
Business logic implementation. This is where the actual decision logic lives.

```python
"""
<Module Name> Engine

Core business logic for <module_name>.
"""

import logging
from typing import Any, Dict, List

from .models import <ModuleName>Input, <ModuleName>Output
from .config import <ModuleName>Config

logger = logging.getLogger(__name__)


class <ModuleName>Engine:
    """
    Core business logic for <module_name>.
    
    This class contains the actual decision-making logic.
    """
    
    def __init__(self, config: <ModuleName>Config):
        """
        Initialize the engine.
        
        Args:
            config: Module configuration
        """
        self.config = config
        
        # TODO(platform): Initialize models, load weights, etc.
        # This is where Hugging Face models would be loaded
    
    def process(self, input_data: <ModuleName>Input) -> <ModuleName>Output:
        """
        Process input and generate recommendation.
        
        Args:
            input_data: Validated input data
            
        Returns:
            <ModuleName>Output with recommendation
        """
        logger.info("Processing <module_name> request")
        
        # TODO(platform): Implement actual business logic
        # This is where you would:
        # 1. Extract features
        # 2. Run model inference
        # 3. Apply business rules
        # 4. Generate explanation
        
        # Placeholder implementation
        recommendation = self._generate_recommendation(input_data)
        confidence = self._calculate_confidence(input_data)
        reasoning = self._generate_reasoning(input_data, recommendation)
        alternatives = self._generate_alternatives(input_data, recommendation)
        
        return <ModuleName>Output(
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=alternatives,
            metadata={"version": "1.0.0"}
        )
    
    def _generate_recommendation(self, input_data: <ModuleName>Input) -> Any:
        """Generate primary recommendation."""
        # TODO(platform): Implement recommendation logic
        return "placeholder_recommendation"
    
    def _calculate_confidence(self, input_data: <ModuleName>Input) -> float:
        """Calculate confidence score."""
        # TODO(platform): Implement confidence calculation
        return 0.85
    
    def _generate_reasoning(self, input_data: <ModuleName>Input, recommendation: Any) -> str:
        """Generate human-readable explanation."""
        # TODO(platform): Implement explanation generation
        return "Placeholder reasoning"
    
    def _generate_alternatives(self, input_data: <ModuleName>Input, recommendation: Any) -> List[Any]:
        """Generate alternative recommendations."""
        # TODO(platform): Implement alternatives generation
        return []
```

#### `config.py`
Module configuration and settings.

```python
"""
<Module Name> Configuration

Configuration settings for <module_name>.
"""

from typing import Optional
from pydantic import BaseModel, Field


class <ModuleName>Config(BaseModel):
    """
    Configuration for <module_name>.
    
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
    
    # Feature flags
    enable_feature_x: bool = Field(
        default=True,
        description="Enable feature X"
    )
    
    # Performance settings
    max_processing_time_seconds: int = Field(
        default=30,
        ge=1,
        description="Maximum processing time"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_name": "fnol_classifier_v2",
                "model_version": "2.1.0",
                "confidence_threshold": 0.90,
                "enable_feature_x": True,
                "max_processing_time_seconds": 30
            }
        }
```

#### `README.md`
Module documentation.

```markdown
# <Module Name>

## Overview

Brief description of what this module does.

## Decision Type

- **Primary**: ADVISORY / BOUNDED / SIMULATION
- **Supported**: List all supported decision types

## Input Schema

Describe the input fields and their requirements.

## Output Schema

Describe the output fields and their meaning.

## Business Logic

Explain the decision-making logic at a high level.

## Human-in-the-Loop

Describe when human approval is required:
- Confidence below X%
- Specific conditions
- Regulatory requirements

## Usage Example

```python
from modules.<module_name> import <ModuleName>Service, <ModuleName>Input
from core.decision_engine import DecisionContext, DecisionType

# Initialize service
service = <ModuleName>Service()

# Create input
input_data = <ModuleName>Input(
    field1="value1",
    field2=42
)

# Create context
context = DecisionContext(
    user_id="user@example.com",
    user_role="adjuster"
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

Describe configuration options.

## Testing

```bash
pytest modules/<module_name>/tests/
```

## Version History

- **v1.0.0** (YYYY-MM-DD) - Initial implementation
```

## Module Import Rules

### ✅ ALLOWED

```python
# Importing from core
from core.decision_engine import DecisionOrchestrator, DecisionType
from core.policy_engine import PolicyEnforcer
from core.audit_logging import AuditLogger
from core.security import AuthorizationManager, Permission

# Standard library
from typing import Any, Dict, List, Optional
import logging

# Pydantic
from pydantic import BaseModel, Field

# Hugging Face (ONLY in modules, NEVER in core)
from transformers import AutoModel, AutoTokenizer
import torch
```

### ❌ FORBIDDEN

```python
# Importing from other modules
from modules.fnol_triage import FNOLService  # ❌ NEVER
from modules.fraud_detection import *        # ❌ NEVER

# Importing from spaces
from spaces.fnol_space import *              # ❌ NEVER
import gradio                                # ❌ NEVER (use in spaces only)
```

## Human-in-the-Loop Requirements

All modules MUST implement human-in-the-loop hooks:

1. **Confidence-based approval**
   - Decisions below confidence threshold require approval
   - Threshold configurable per module

2. **Exception escalation**
   - Out-of-bounds inputs escalate to human
   - Unexpected patterns escalate to human

3. **Regulatory compliance**
   - High-value decisions require approval
   - Sensitive decisions require approval

4. **Explainability**
   - All decisions must include reasoning
   - Reasoning must be human-readable
   - Reasoning must reference input factors

## Testing Requirements

All modules MUST have:

1. **Unit tests** (>80% coverage)
   - Test business logic in isolation
   - Test input validation
   - Test error handling

2. **Integration tests**
   - Test with core services
   - Test end-to-end flow
   - Test approval workflows

3. **Example usage**
   - Provide working examples
   - Document common use cases
   - Show error handling

## Module Checklist

When creating a new module:

- [ ] Follow standard structure (see above)
- [ ] Define input/output schemas with Pydantic
- [ ] Implement service interface
- [ ] Implement business logic in engine
- [ ] Use core services (orchestrator, policy, audit)
- [ ] Add human-in-the-loop hooks
- [ ] Write comprehensive README
- [ ] Add unit tests (>80% coverage)
- [ ] Add integration tests
- [ ] Add usage examples
- [ ] Document configuration options
- [ ] Add TODO markers for deferred work
- [ ] No imports from other modules
- [ ] No imports from spaces

## Migration from Hugging Face Spaces

When migrating logic from existing Spaces:

1. **Extract business logic**
   - Identify core decision-making code
   - Move to `engine.py`
   - Remove UI dependencies

2. **Define schemas**
   - Create Pydantic models for inputs
   - Create Pydantic models for outputs
   - Add validation rules

3. **Integrate with core**
   - Use DecisionOrchestrator
   - Use PolicyEnforcer
   - Use AuditLogger

4. **Add tests**
   - Unit tests for engine
   - Integration tests for service
   - Example usage

5. **Update Space**
   - Space becomes thin UI layer
   - Space imports from module
   - Space has NO business logic

## Example: Complete Module

See `modules/fnol_triage/` for a complete reference implementation.
