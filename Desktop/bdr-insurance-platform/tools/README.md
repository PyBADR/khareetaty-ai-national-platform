# BDR Insurance Platform - Development Tools

**Purpose:** Internal utilities, scripts, and CLIs for platform development, testing, and maintenance.

---

## Overview

This directory contains development tools that help maintain code quality, enforce architectural boundaries, and streamline common workflows.

**Key Principles:**
- Tools are for developers, not end users
- Tools enforce platform governance
- Tools are tested and documented
- Tools integrate with CI/CD pipelines

---

## Available Tools

### 1. Import Checker (`check_imports.py`)

**Purpose:** Enforce architectural boundaries by detecting import violations.

**Rules Enforced:**
- Core modules NEVER import from modules or spaces
- Modules NEVER import from spaces
- Spaces NEVER import from other spaces
- No circular dependencies

**Usage:**
```bash
python tools/check_imports.py

# Check specific directory
python tools/check_imports.py --path modules/fnol_triage

# Fail on first violation (for CI/CD)
python tools/check_imports.py --strict
```

**Example Output:**
```
✓ core/decision_engine/__init__.py - OK
✓ core/policy_engine/enforcer.py - OK
✗ modules/fnol_triage/service.py - VIOLATION
  Line 5: from spaces.fnol_space.utils import format_output
  Reason: Modules cannot import from spaces

Summary: 2 passed, 1 failed
```

**CI/CD Integration:**
```yaml
# .github/workflows/ci.yml
- name: Check Import Boundaries
  run: python tools/check_imports.py --strict
```

---

### 2. Schema Validator (`validate_schemas.py`)

**Purpose:** Validate all JSON schemas and ensure they follow platform standards.

**Checks:**
- Valid JSON Schema draft-07 syntax
- Required fields present (title, description, type)
- Examples are valid against schema
- Version numbering follows semver
- No breaking changes without version bump

**Usage:**
```bash
python tools/validate_schemas.py

# Validate specific schema
python tools/validate_schemas.py --schema datasets/schemas/fnol_v1.json

# Check for breaking changes
python tools/validate_schemas.py --compare-versions fnol_v1.json fnol_v2.json
```

---

### 3. Decision Simulator (`simulate_decision.py`)

**Purpose:** Test decision workflows end-to-end without deploying.

**Features:**
- Load sample data from datasets/synthetic/
- Execute decision through full stack (core + module)
- Display audit trail and governance checks
- Measure performance

**Usage:**
```bash
# Simulate FNOL triage
python tools/simulate_decision.py \
  --module fnol_triage \
  --input datasets/synthetic/fnol_sample.json \
  --user-id test_adjuster

# Output:
Decision ID: dec_fnol_20260120_123456
Module: fnol_triage
Processing Time: 145ms
Requires Review: Yes
Review Reason: High-value claim ($75,000)
Audit Log: /tmp/audit_dec_fnol_20260120_123456.json
```

---

### 4. Benchmark Runner (`run_benchmarks.py`)

**Purpose:** Execute benchmark evaluations and track performance over time.

**Features:**
- Run benchmarks from datasets/benchmarks/
- Calculate metrics (accuracy, precision, recall, F1)
- Compare against baseline
- Detect regressions
- Generate reports

**Usage:**
```bash
# Run all benchmarks
python tools/run_benchmarks.py

# Run specific module benchmarks
python tools/run_benchmarks.py --module fraud_detection

# Compare against baseline
python tools/run_benchmarks.py --baseline results/baseline_v1.0.json

# Save results
python tools/run_benchmarks.py --output results/run_20260120.json
```

**Example Output:**
```
Benchmark: fraud_detection_v1
Dataset: 500 cases

Metrics:
  Accuracy: 0.94 (baseline: 0.92) ✓ +2%
  Precision: 0.89 (baseline: 0.88) ✓ +1%
  Recall: 0.91 (baseline: 0.90) ✓ +1%
  F1 Score: 0.90 (baseline: 0.89) ✓ +1%

Performance:
  Avg Latency: 245ms (baseline: 280ms) ✓ -12%
  P95 Latency: 450ms (baseline: 520ms) ✓ -13%

Result: PASS (no regressions detected)
```

---

### 5. TODO Aggregator (`aggregate_todos.py`)

**Purpose:** Collect all TODO/FIXME/NOTE markers across codebase.

**Features:**
- Scan all Python files for structured markers
- Group by category (platform, security, governance, etc.)
- Generate markdown report
- Track technical debt

**Usage:**
```bash
# Generate TODO report
python tools/aggregate_todos.py --output docs/TODO_REPORT.md

# Filter by category
python tools/aggregate_todos.py --category security

# Show only high-priority items
python tools/aggregate_todos.py --priority high
```

**Example Output:**
```markdown
# Platform TODO Report
Generated: 2026-01-20

## Security (3 items)
- [ ] TODO(security): Implement field-level encryption for PII
      File: core/security/encryption.py:45
- [ ] FIXME(security): Add rate limiting to API endpoints
      File: modules/fnol_triage/service.py:78

## Platform (5 items)
- [ ] TODO(platform): Add multi-tenancy support
      File: core/decision_engine/orchestrator.py:120
```

---

### 6. Module Generator (`generate_module.py`)

**Purpose:** Scaffold new business modules from template.

**Features:**
- Create complete module structure
- Generate schemas, service, engine, tests
- Follow platform patterns
- Include documentation

**Usage:**
```bash
# Generate new module
python tools/generate_module.py \
  --name claims_settlement \
  --description "Claims settlement decision support"

# Output:
Created: modules/claims_settlement/
  ├── __init__.py
  ├── schemas.py
  ├── service.py
  ├── engine.py
  ├── models.py
  ├── tests/
  │   ├── test_service.py
  │   └── test_engine.py
  └── README.md

Next steps:
1. Implement business logic in engine.py
2. Define schemas in schemas.py
3. Add tests
4. Update docs/architecture.md
```

---

### 7. Dependency Analyzer (`analyze_dependencies.py`)

**Purpose:** Analyze and visualize module dependencies.

**Features:**
- Generate dependency graph
- Detect circular dependencies
- Calculate coupling metrics
- Identify unused imports

**Usage:**
```bash
# Generate dependency graph
python tools/analyze_dependencies.py --output deps.png

# Check for circular dependencies
python tools/analyze_dependencies.py --check-circular

# Calculate coupling metrics
python tools/analyze_dependencies.py --metrics
```

---

### 8. Audit Log Viewer (`view_audit_logs.py`)

**Purpose:** Query and analyze audit logs.

**Features:**
- Search by decision ID, module, user, date range
- Display decision context and results
- Export to CSV/JSON
- Generate compliance reports

**Usage:**
```bash
# View recent decisions
python tools/view_audit_logs.py --recent 10

# Search by decision ID
python tools/view_audit_logs.py --decision-id dec_fnol_20260120_123456

# Filter by module and date
python tools/view_audit_logs.py \
  --module fraud_detection \
  --start-date 2026-01-01 \
  --end-date 2026-01-20

# Export to CSV
python tools/view_audit_logs.py --export audit_report.csv
```

---

## Development Workflow Integration

### Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check import boundaries
python tools/check_imports.py --strict || exit 1

# Validate schemas
python tools/validate_schemas.py || exit 1

# Run fast tests
pytest tests/unit/ -v || exit 1

echo "✓ Pre-commit checks passed"
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check Import Boundaries
        run: python tools/check_imports.py --strict
      
      - name: Validate Schemas
        run: python tools/validate_schemas.py
      
      - name: Run Benchmarks
        run: python tools/run_benchmarks.py --baseline results/baseline.json
      
      - name: Aggregate TODOs
        run: python tools/aggregate_todos.py --output TODO_REPORT.md
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: reports
          path: |
            TODO_REPORT.md
            results/
```

---

## Tool Development Guidelines

### 1. Structure
```python
#!/usr/bin/env python3
"""
Tool Name: Brief description

Usage:
    python tools/tool_name.py [options]

Examples:
    python tools/tool_name.py --help
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Tool description")
    # Add arguments
    args = parser.parse_args()
    
    # Tool logic
    
    return 0  # Success

if __name__ == "__main__":
    sys.exit(main())
```

### 2. Error Handling
- Use clear error messages
- Exit with appropriate codes (0=success, 1=error)
- Log to stderr for errors, stdout for output

### 3. Testing
- All tools should have tests in `tools/tests/`
- Test both success and failure cases
- Mock external dependencies

### 4. Documentation
- Include docstrings
- Provide usage examples
- Document exit codes

---

## TODO: Future Tools

### TODO(tools): Performance Profiler
```bash
python tools/profile_decision.py --module fnol_triage --iterations 1000
```

### TODO(tools): Data Generator
```bash
python tools/generate_synthetic_data.py \
  --schema datasets/schemas/fnol_v1.json \
  --count 1000 \
  --output datasets/synthetic/fnol_large.json
```

### TODO(tools): Migration Helper
```bash
python tools/migrate_schema.py \
  --from fnol_v1.json \
  --to fnol_v2.json \
  --data datasets/synthetic/fnol_sample.json
```

### TODO(tools): Security Scanner
```bash
python tools/scan_security.py --check-all
```

### TODO(tools): Documentation Generator
```bash
python tools/generate_docs.py --output docs/api/
```

---

## Contributing

When adding new tools:

1. Follow the structure guidelines above
2. Add tests in `tools/tests/`
3. Update this README
4. Add to CI/CD pipeline if appropriate
5. Document in `docs/lifecycle.md` if it affects workflows

---

**Tool Maintenance:** Platform Team  
**Review Cycle:** Quarterly  
**Next Review:** April 20, 2026
