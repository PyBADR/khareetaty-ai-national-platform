# Audit Logging Module

## Overview

The Audit Logging module provides comprehensive audit trail capabilities for all decision-making processes in the BDR Insurance Platform.

**Source**: Extracted from `insurance-hf-project/create_gradio_space.py`

## Key Features

1. **Complete Audit Trail**: Every decision, validation, and override is logged
2. **Structured Logging**: Consistent schema for all audit entries
3. **Multiple Storage Backends**: In-memory, file-based, or custom storage
4. **Queryable**: Filter and search audit logs by multiple criteria
5. **Export Capabilities**: Export to JSON or CSV for analysis
6. **Compliance Ready**: Meets regulatory audit requirements

## Components

### 1. AuditLogger (`logger.py`)

Main interface for logging audit events.

**Key Methods**:
- `log_decision()` - Log a complete decision with all context
- `log_validation()` - Log validation events
- `log_compliance_check()` - Log compliance checks
- `log_override()` - Log when humans override system recommendations
- `get_entries()` - Query audit entries with filters
- `get_decision_trail()` - Get complete trail for a specific decision
- `export_entries()` - Export entries in JSON or CSV format

### 2. AuditEntry (`logger.py`)

Structured audit log entry containing:

**Core Fields**:
- `timestamp` - When the event occurred
- `entry_id` - Unique identifier
- `entry_type` - Type of event (decision, validation, override, etc.)
- `level` - Severity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Decision Context**:
- `decision_id` - Decision identifier
- `user_id` - User who made the decision
- `session_id` - Session identifier

**Input/Output**:
- `input_data` - Input data for the decision
- `output_data` - Output/result of the decision

**Risk Metrics**:
- `risk_score` - Risk score (0-100)
- `risk_level` - Risk level (LOW/MEDIUM/HIGH)
- `confidence` - Model confidence (0-1)
- `uncertainty_flag` - Whether uncertainty is flagged

**Human Oversight**:
- `human_decision` - Human's final decision
- `human_justification` - Human's justification
- `oversight_level` - Level of oversight applied

**Evidence & Compliance**:
- `missing_evidence` - List of missing evidence
- `documentation_status` - Documentation completeness
- `compliance_status` - Compliance check result
- `compliance_violations` - List of violations

### 3. Storage Backends (`storage.py`)

**InMemoryAuditStorage**
- Fast, simple storage for development/testing
- Data lost on restart
- Not suitable for production

**FileAuditStorage**
- Persistent file-based storage (JSON lines)
- Suitable for small-scale deployments
- Easy backup and export

**Future**: Database storage (PostgreSQL, MongoDB, Elasticsearch)

## Usage Examples

### Example 1: Basic Decision Logging

```python
from core.audit_logging import AuditLogger

logger = AuditLogger()

# Log a decision
entry = logger.log_decision(
    decision_id="DEC-12345",
    input_data={
        'claim_id': 'CLM-67890',
        'claim_amount': 15000,
        'claimant_age': 42
    },
    output_data={
        'recommendation': 'APPROVE',
        'reasoning': 'Low risk, complete documentation'
    },
    risk_score=25.5,
    risk_level='LOW',
    confidence=0.89,
    uncertainty_flag=False,
    human_decision='APPROVED',
    human_justification='Reviewed all evidence, claim is legitimate',
    oversight_level='REQUIRED',
    user_id='adjuster_001'
)

print(f"Logged entry: {entry.entry_id}")
```

### Example 2: Query Audit Trail

```python
from datetime import datetime, timedelta

# Get all decisions from the last 24 hours
recent_entries = logger.get_entries(
    entry_type='decision',
    start_time=datetime.now() - timedelta(days=1)
)

print(f"Found {len(recent_entries)} recent decisions")

# Get complete trail for a specific decision
trail = logger.get_decision_trail('DEC-12345')
for entry in trail:
    print(f"{entry.timestamp}: {entry.entry_type} - {entry.level.value}")
```

### Example 3: Log Human Override

```python
# Log when human overrides system recommendation
entry = logger.log_override(
    decision_id="DEC-12345",
    original_recommendation="REJECT",
    human_override="APPROVE",
    justification="System flagged minor discrepancy, but claimant provided additional evidence that resolves the issue.",
    user_id="senior_adjuster_005"
)

print("Override logged with justification")
```

### Example 4: Export Audit Logs

```python
# Export all entries from last month as JSON
json_export = logger.export_entries(
    start_time=datetime.now() - timedelta(days=30),
    format='json'
)

with open('audit_export.json', 'w') as f:
    f.write(json_export)

# Export as CSV
csv_export = logger.export_entries(
    start_time=datetime.now() - timedelta(days=30),
    format='csv'
)

with open('audit_export.csv', 'w') as f:
    f.write(csv_export)
```

### Example 5: File-Based Storage

```python
from core.audit_logging import AuditLogger, FileAuditStorage

# Use file-based storage for persistence
storage = FileAuditStorage('logs/audit.jsonl')
logger = AuditLogger(storage=storage)

# Logs are now persisted to file
logger.log_decision(...)

# Query from file
entries = logger.get_entries(limit=10)
```

### Example 6: Get Statistics

```python
stats = logger.get_statistics()

print(f"Total entries: {stats['total_entries']}")
print(f"By type: {stats['by_type']}")
print(f"By level: {stats['by_level']}")
print(f"By user: {stats['by_user']}")
```

## Integration with Decision Engine

The Audit Logger integrates seamlessly with the Decision Engine:

```python
from core.decision_engine import DecisionOrchestrator
from core.audit_logging import AuditLogger

audit_logger = AuditLogger()

orchestrator = DecisionOrchestrator(
    policy_engine=policy_engine,
    audit_logger=audit_logger,  # Inject audit logger
    telemetry=telemetry
)

# Decisions are automatically logged
result = orchestrator.execute_decision(...)
```

## Compliance & Regulatory Requirements

### Audit Trail Requirements

The audit logging module meets the following requirements:

1. **Completeness**: All decisions and actions are logged
2. **Immutability**: Entries cannot be modified after creation
3. **Traceability**: Complete trail from input to output
4. **Accountability**: User identification for all actions
5. **Timestamp**: Precise timing of all events
6. **Retention**: Configurable retention policies

### Regulatory Standards

- **SOC 2**: Audit logging for security and availability
- **ISO 27001**: Information security audit trails
- **GDPR**: Data processing audit requirements
- **State Insurance Regulations**: Claims processing audit trails
- **Fair Claims Settlement Practices**: Decision documentation

## Storage Recommendations

### Development
- Use `InMemoryAuditStorage` for fast iteration
- No persistence needed

### Testing
- Use `FileAuditStorage` for test audit trails
- Easy to inspect and verify

### Production
- **Small Scale**: `FileAuditStorage` with log rotation
- **Medium Scale**: PostgreSQL with partitioning
- **Large Scale**: Elasticsearch or dedicated audit database
- **Compliance**: Immutable storage (S3 with versioning, WORM storage)

## Performance Considerations

1. **Async Logging**: Consider async writes for high-volume scenarios
2. **Batching**: Batch writes to reduce I/O overhead
3. **Indexing**: Index frequently queried fields (decision_id, user_id, timestamp)
4. **Archival**: Archive old entries to cold storage
5. **Partitioning**: Partition by date for efficient queries

## Security

1. **Access Control**: Restrict audit log access to authorized users
2. **Encryption**: Encrypt sensitive data in audit logs
3. **Integrity**: Use checksums or signatures to prevent tampering
4. **Retention**: Define and enforce retention policies
5. **Backup**: Regular backups of audit logs

## TODO

- [ ] Implement PostgreSQL storage backend
- [ ] Implement MongoDB storage backend
- [ ] Add async logging support
- [ ] Add log rotation for FileAuditStorage
- [ ] Implement audit log integrity verification
- [ ] Add support for encrypted storage
- [ ] Create audit log analysis tools
- [ ] Add automated compliance reporting

## Changelog

### v1.0.0 (2026-01-20)
- Initial extraction from insurance-hf-project
- Implemented AuditLogger with comprehensive logging methods
- Implemented AuditEntry with complete decision context
- Implemented InMemoryAuditStorage and FileAuditStorage
- Full documentation and usage examples
