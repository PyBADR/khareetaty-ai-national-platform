"""
BDR Insurance Platform - Core Layer

This package contains reusable, domain-agnostic platform services that power
all business modules. Core services must never import from modules or spaces.

Core Services:
- decision_engine: Orchestrates decision workflows
- policy_engine: Enforces business rules and constraints
- governance: Manages human-in-the-loop controls
- audit_logging: Immutable audit trails
- telemetry: Observability and monitoring
- security: Authentication, authorization, encryption

Version: 1.0.0
"""

__version__ = "1.0.0"

# Core service imports will be added as modules are implemented
__all__ = [
    "decision_engine",
    "policy_engine",
    "governance",
    "audit_logging",
    "telemetry",
    "security",
]
