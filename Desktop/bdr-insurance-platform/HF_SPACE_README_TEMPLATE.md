# [Space Name] - Interface Adapter

⚠️ **This Space is an interface-only adapter.**

All decision logic, authority enforcement, and evaluation are implemented in the BDR GitHub reference architecture.

This Space cannot execute production decisions.

---

## What This Space Does

- Visualizes decision inputs and outputs
- Simulates decision flows
- Renders user interface

## What This Space Does NOT Do

- Execute production decisions
- Define authority or ownership
- Bypass evaluation gates
- Contain business logic

---

## Architecture

This Space imports from:
```python
from bdr_insurance_platform.modules.[module_name] import service
from bdr_insurance_platform.core.execution import ExecutionEnvironment

env = ExecutionEnvironment.SIMULATION

def run(input_data):
    return service.simulate(input_data, env=env)
```

**All governance logic lives in GitHub.**

---

## Reference Architecture

GitHub Repository: `bdr-insurance-decision-platform`  
Status: FROZEN  
Version: reference-v1.0

---

## Disclaimer

This is a simulation interface only. Production decisions require:
- Explicit ownership
- Valid authority anchor
- Evaluation clearance
- Execution boundary enforcement

None of these exist in Hugging Face Spaces.
