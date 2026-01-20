# BDR Insurance Platform - System Architecture

**Version:** 1.0  
**Last Updated:** January 2026  
**Status:** Production-Ready Design

---

## 1. Executive Summary

The BDR Insurance Decision Intelligence Platform is an enterprise-grade, open-source SaaS architecture designed for regulated insurance markets. This document defines the system architecture, component interactions, data flows, and deployment patterns.

**Key Architectural Goals:**
- **Separation of Concerns**: Clean boundaries between platform, products, and presentation
- **Auditability**: Every decision is traceable and explainable
- **Scalability**: Designed for cloud-native deployment (Docker/Kubernetes)
- **Maintainability**: Modular design prevents technical debt accumulation
- **Regulatory Compliance**: Built-in governance and human oversight

---

## 2. High-Level Architecture

### 2.1 System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│              (Hugging Face Spaces - Thin UI)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Hub    │  │   FNOL   │  │  Fraud   │  │   IFRS   │   │
│  │  Space   │  │  Space   │  │  Space   │  │  Space   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCT MODULES LAYER                     │
│              (Business Logic & Domain Models)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   FNOL   │  │  Fraud   │  │   IFRS   │  │Underwrite│   │
│  │  Triage  │  │Detection │  │ Accrual  │  │  Score   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Service Interfaces
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    CORE PLATFORM LAYER                       │
│              (Reusable Platform Services)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Decision  │  │  Policy  │  │Governance│  │  Audit   │   │
│  │ Engine   │  │  Engine  │  │          │  │ Logging  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐                                │
│  │Telemetry │  │ Security │                                │
│  └──────────┘  └──────────┘                                │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │Synthetic │  │Benchmarks│  │ Schemas  │                  │
│  │ Datasets │  │          │  │          │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Dependency Rules

**STRICT ENFORCEMENT:**

1. **Presentation Layer (Spaces)**
   - ✅ CAN import from: Product Modules
   - ❌ CANNOT import from: Core (must go through modules)
   - ❌ CANNOT contain: Business logic, model inference, data processing

2. **Product Modules Layer**
   - ✅ CAN import from: Core Platform
   - ❌ CANNOT import from: Other modules (use events/APIs for inter-module communication)
   - ❌ CANNOT import from: Spaces

3. **Core Platform Layer**
   - ✅ CAN import from: Standard libraries only
   - ❌ CANNOT import from: Modules or Spaces
   - ❌ CANNOT contain: Business-specific logic

4. **Data Layer**
   - ✅ CAN be accessed by: All layers
   - ❌ CANNOT contain: Logic or code

---

## 3. Core Platform Components

### 3.1 Decision Engine

**Responsibility:** Orchestrates decision workflows and manages decision lifecycle.

**Key Functions:**
```python
# core/decision_engine/orchestrator.py

class DecisionOrchestrator:
    def execute_decision(
        self,
        decision_type: DecisionType,
        input_data: Dict[str, Any],
        context: DecisionContext
    ) -> DecisionResult:
        """
        Orchestrates a decision workflow.
        
        Args:
            decision_type: ADVISORY | BOUNDED | SIMULATION
            input_data: Input parameters for the decision
            context: User, timestamp, trace_id, etc.
            
        Returns:
            DecisionResult with outcome, confidence, reasoning
        """
        pass
```

**Decision Types:**
- **ADVISORY**: Provides recommendations, human makes final decision
- **BOUNDED**: Automated within defined constraints, escalates exceptions
- **SIMULATION**: What-if analysis, no real-world impact

**Interfaces:**
- `execute_decision()`: Main entry point for all decisions
- `get_decision_status()`: Query decision state
- `explain_decision()`: Generate explanation for audit

### 3.2 Policy Engine

**Responsibility:** Enforces business rules, constraints, and regulatory requirements.

**Key Functions:**
```python
# core/policy_engine/enforcer.py

class PolicyEnforcer:
    def validate_decision(
        self,
        decision: Decision,
        policies: List[Policy]
    ) -> ValidationResult:
        """
        Validates a decision against active policies.
        
        Returns:
            ValidationResult with pass/fail and violations
        """
        pass
    
    def check_constraints(
        self,
        input_data: Dict[str, Any],
        constraints: List[Constraint]
    ) -> ConstraintCheckResult:
        """
        Checks input data against defined constraints.
        """
        pass
```

**Policy Types:**
- **Regulatory**: GDPR, IFRS 17, Solvency II compliance
- **Business**: Underwriting guidelines, pricing rules
- **Operational**: SLAs, performance thresholds

### 3.3 Governance

**Responsibility:** Manages human-in-the-loop controls and approval workflows.

**Key Functions:**
```python
# core/governance/human_in_loop.py

class GovernanceController:
    def require_approval(
        self,
        decision: Decision,
        approval_rules: ApprovalRules
    ) -> ApprovalRequest:
        """
        Routes decision for human approval based on rules.
        """
        pass
    
    def escalate_decision(
        self,
        decision: Decision,
        reason: EscalationReason
    ) -> EscalationTicket:
        """
        Escalates decision to higher authority.
        """
        pass
```

**Approval Levels:**
- **L1**: Automated (within bounds)
- **L2**: Supervisor review required
- **L3**: Manager approval required
- **L4**: Executive sign-off required

### 3.4 Audit Logging

**Responsibility:** Immutable audit trails for all decisions and actions.

**Key Functions:**
```python
# core/audit_logging/logger.py

class AuditLogger:
    def log_decision(
        self,
        decision: Decision,
        context: DecisionContext,
        outcome: DecisionOutcome
    ) -> AuditRecord:
        """
        Creates immutable audit record.
        
        Records:
            - Input data (sanitized)
            - Decision reasoning
            - Model versions used
            - User/system context
            - Timestamp and trace_id
        """
        pass
```

**Audit Record Schema:**
```json
{
  "audit_id": "uuid",
  "trace_id": "uuid",
  "timestamp": "ISO8601",
  "decision_type": "ADVISORY|BOUNDED|SIMULATION",
  "module": "fnol_triage",
  "user_id": "user@example.com",
  "input_hash": "sha256",
  "output_hash": "sha256",
  "model_versions": ["model_v1.2.3"],
  "reasoning": "...",
  "approval_chain": [],
  "compliance_flags": []
}
```

### 3.5 Telemetry

**Responsibility:** Observability, metrics, and performance monitoring.

**Key Metrics:**
- Decision latency (p50, p95, p99)
- Decision volume by type
- Approval rates and escalation rates
- Model performance metrics
- System health indicators

**Integration Points:**
- Prometheus for metrics
- Grafana for dashboards
- OpenTelemetry for distributed tracing

### 3.6 Security

**Responsibility:** Authentication, authorization, encryption, and access control.

**Key Functions:**
```python
# core/security/auth.py

class SecurityManager:
    def authenticate_user(self, credentials: Credentials) -> User:
        """Authenticates user identity."""
        pass
    
    def authorize_action(
        self,
        user: User,
        action: Action,
        resource: Resource
    ) -> bool:
        """Checks if user can perform action on resource."""
        pass
    
    def encrypt_sensitive_data(self, data: Any) -> EncryptedData:
        """Encrypts PII and sensitive information."""
        pass
```

**Security Controls:**
- **Authentication**: OAuth2/OIDC integration
- **Authorization**: Role-Based Access Control (RBAC)
- **Encryption**: At-rest and in-transit
- **Data Masking**: PII protection in logs and audit trails

---

## 4. Product Module Architecture

### 4.1 Module Structure

Each product module follows this standard structure:

```
modules/fnol_triage/
├── __init__.py
├── service.py           # Public service interface
├── models.py            # Data models and contracts
├── business_logic.py    # Domain-specific logic
├── config.py            # Module configuration
├── tests/               # Unit and integration tests
└── README.md            # Module documentation
```

### 4.2 Service Interface Pattern

**Every module exposes a clean service interface:**

```python
# modules/fnol_triage/service.py

from core.decision_engine import DecisionOrchestrator
from core.governance import GovernanceController
from .models import FNOLInput, FNOLOutput

class FNOLTriageService:
    def __init__(
        self,
        decision_engine: DecisionOrchestrator,
        governance: GovernanceController
    ):
        self.decision_engine = decision_engine
        self.governance = governance
    
    def run_triage(
        self,
        claim_data: FNOLInput,
        user_context: UserContext
    ) -> FNOLOutput:
        """
        Triages a First Notice of Loss claim.
        
        Args:
            claim_data: Claim details (injury, property, etc.)
            user_context: User making the request
            
        Returns:
            FNOLOutput with triage decision, priority, routing
        """
        # 1. Validate input
        validated_input = self._validate_input(claim_data)
        
        # 2. Execute decision via core engine
        decision = self.decision_engine.execute_decision(
            decision_type=DecisionType.ADVISORY,
            input_data=validated_input,
            context=user_context
        )
        
        # 3. Check if human approval needed
        if decision.confidence < 0.8:
            self.governance.require_approval(decision)
        
        # 4. Return structured output
        return FNOLOutput.from_decision(decision)
```

### 4.3 Input/Output Contracts

**All modules define strict contracts:**

```python
# modules/fnol_triage/models.py

from pydantic import BaseModel, Field
from typing import Literal

class FNOLInput(BaseModel):
    """Input contract for FNOL triage."""
    
    claim_id: str = Field(..., description="Unique claim identifier")
    claim_type: Literal["injury", "property", "auto"] = Field(...)
    severity: int = Field(..., ge=1, le=10)
    description: str = Field(..., max_length=5000)
    claimant_info: dict = Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "claim_id": "CLM-2026-001",
                "claim_type": "injury",
                "severity": 7,
                "description": "Slip and fall incident...",
                "claimant_info": {...}
            }
        }

class FNOLOutput(BaseModel):
    """Output contract for FNOL triage."""
    
    triage_decision: Literal["urgent", "standard", "low_priority"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_adjuster: str
    estimated_reserve: float
    reasoning: str
    requires_approval: bool
```

---

## 5. Data Flow Architecture

### 5.1 Decision Flow

```
User Input (Space)
    ↓
Module Service Interface
    ↓
Input Validation (Module)
    ↓
Decision Engine (Core)
    ↓
Policy Enforcement (Core)
    ↓
Governance Check (Core)
    ↓
Audit Logging (Core)
    ↓
Result to User (Space)
```

### 5.2 Approval Flow

```
Decision Requires Approval
    ↓
Governance Controller
    ↓
Approval Request Created
    ↓
Notification to Approver
    ↓
Approver Reviews Decision
    ↓
Approve/Reject/Escalate
    ↓
Audit Log Updated
    ↓
Result Returned to User
```

### 5.3 Data Lineage

**Every decision tracks:**
- Input data source and version
- Model versions used
- Policy versions applied
- Intermediate computation steps
- Final output and confidence

**Stored in audit logs for:**
- Regulatory compliance
- Model debugging
- Performance analysis
- Explainability

---

## 6. Deployment Architecture

### 6.1 Local Development

```
Developer Machine
├── VS Code
├── Python 3.10+
├── Local PostgreSQL (audit logs)
├── Local Redis (caching)
└── pytest (testing)
```

### 6.2 Staging Environment

```
Docker Compose
├── API Service (FastAPI)
├── PostgreSQL (audit database)
├── Redis (cache)
├── Prometheus (metrics)
└── Grafana (dashboards)
```

### 6.3 Production Environment

```
Kubernetes Cluster
├── API Pods (auto-scaling)
├── Worker Pods (async processing)
├── PostgreSQL (managed service)
├── Redis (managed service)
├── S3 (model artifacts)
├── CloudWatch/Datadog (monitoring)
└── Load Balancer (ingress)
```

### 6.4 Hugging Face Spaces Deployment

**Spaces are deployed separately:**

```
Hugging Face Space
├── app.py (Gradio/Streamlit UI)
├── requirements.txt (includes bdr-platform package)
└── README.md (space documentation)
```

**Spaces connect to platform via:**
- REST API (production)
- Direct import (development/demo)

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
User → OAuth2 Provider → JWT Token → API Gateway → Service
```

### 7.2 Authorization Model

**Role-Based Access Control (RBAC):**

| Role | Permissions |
|------|-------------|
| Viewer | Read decisions, view dashboards |
| Analyst | Create advisory decisions |
| Adjuster | Create bounded decisions (within limits) |
| Manager | Approve escalated decisions |
| Admin | Configure policies, manage users |

### 7.3 Data Protection

- **PII Encryption**: AES-256 at rest
- **TLS 1.3**: All data in transit
- **Data Masking**: Logs and audit trails
- **Access Logging**: All data access tracked

---

## 8. Scalability Considerations

### 8.1 Horizontal Scaling

- **Stateless Services**: All API services are stateless
- **Database Sharding**: Audit logs partitioned by date
- **Caching Strategy**: Redis for frequently accessed data
- **Async Processing**: Celery for long-running tasks

### 8.2 Performance Targets

| Metric | Target |
|--------|--------|
| API Latency (p95) | < 500ms |
| Decision Throughput | 1000 decisions/sec |
| Audit Log Write | < 50ms |
| Dashboard Load | < 2s |

---

## 9. Disaster Recovery

### 9.1 Backup Strategy

- **Audit Logs**: Daily backups, 7-year retention
- **Configuration**: Version controlled in Git
- **Model Artifacts**: Versioned in S3 with replication

### 9.2 Recovery Procedures

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Failover**: Automated to secondary region

---

## 10. Future Architecture Enhancements

### 10.1 Planned Improvements

1. **Event-Driven Architecture**: Kafka for inter-module communication
2. **GraphQL API**: Flexible querying for complex UIs
3. **ML Model Registry**: Centralized model versioning and deployment
4. **A/B Testing Framework**: Controlled rollout of new models
5. **Real-time Streaming**: Apache Flink for real-time decisions

### 10.2 Research Areas

- **Federated Learning**: Privacy-preserving model training
- **Explainable AI**: Enhanced decision reasoning
- **AutoML Integration**: Automated model selection and tuning

---

## 11. Conclusion

This architecture provides a solid foundation for building enterprise-grade insurance decision intelligence products. The clean separation of concerns, strict dependency rules, and built-in governance make this platform suitable for regulated markets while maintaining developer productivity and system maintainability.

**Key Takeaways:**
- Platform services are reusable and domain-agnostic
- Product modules contain business logic with clear contracts
- Spaces are thin UI layers with no business logic
- Every decision is auditable and explainable
- Architecture scales from PoC to production

---

**Document Maintenance:**
- Review quarterly
- Update after major architectural changes
- Version control in Git
