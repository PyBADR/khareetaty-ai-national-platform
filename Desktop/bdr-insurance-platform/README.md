# BDR Insurance Decision Intelligence Platform

## Architectural Status
This repository represents a **frozen reference architecture**.

- No logic may be executed without authority
- No changes are allowed without a new version
- This repository is not a demo, SDK, or product

Purpose:
- Regulatory review
- Architectural benchmarking
- Governance reference

---

**Enterprise-Grade AI SaaS Platform for Regulated Insurance Markets**

---

## 🔒 REFERENCE ARCHITECTURE - FROZEN

**This repository represents a reference-grade decision intelligence architecture.**

**No decision can be executed without explicit ownership, authority, evaluation, and finality enforced at runtime.**

**This system is frozen as an architectural reference and is not intended for direct feature development.**

**Version:** reference-v1.0  
**Status:** FROZEN  
**Date:** January 20, 2026

---

## 🎯 Platform Overview

The BDR Insurance Decision Intelligence Platform is a production-ready, open-source SaaS architecture designed for regulated insurance markets. This platform transforms AI experiments and models into a unified, maintainable, and auditable decision intelligence system.

**Key Principles:**
- **VS Code-First Development**: All code is structured for team collaboration and IDE-native workflows
- **Hugging Face as Presentation Layer**: Spaces are thin UI adapters, not business logic containers
- **Regulated Market Ready**: Built-in governance, audit logging, and human-in-the-loop controls
- **Modular Architecture**: Clean separation between platform services and business products

## 📁 Repository Structure

```
bdr-insurance-platform/
│
├── README.md                 # This file - platform overview
├── pyproject.toml           # Python project configuration & dependencies
├── requirements.txt         # Pinned dependencies for reproducibility
│
├── core/                    # Platform-level reusable services (domain-agnostic)
├── modules/                 # Business products (insurance-specific)
├── datasets/                # Data assets with versioning and schemas
├── spaces/                  # Hugging Face UI adapters (thin presentation layer)
├── docs/                    # Architecture, governance, and compliance documentation
├── tools/                   # Development utilities and scripts
└── .vscode/                 # VS Code workspace settings for team consistency
```

## 🧱 Core Platform Layer (`core/`)

**Purpose**: Reusable, domain-agnostic platform services that power all business modules.

**Responsibilities:**
- **decision_engine/**: Orchestrates decision workflows, manages decision types (advisory/bounded/simulation)
- **policy_engine/**: Enforces business rules, constraints, and regulatory requirements
- **governance/**: Manages human-in-the-loop controls, approval workflows, and oversight
- **audit_logging/**: Immutable audit trails for all decisions and actions
- **telemetry/**: Observability, metrics, and performance monitoring
- **security/**: Authentication, authorization, data encryption, and access control

**Rules:**
- ✅ Must be testable in isolation
- ✅ Must be deterministic and auditable
- ✅ Can be imported by modules
- ❌ NEVER imports from modules or spaces
- ❌ NO Hugging Face-specific logic
- ❌ NO hard-coded business rules

## 📦 Product Modules Layer (`modules/`)

**Purpose**: Business-specific products that deliver insurance decision intelligence.

**Available Modules:**
- **fnol_triage/**: First Notice of Loss intelligent triage and routing
- **fraud_detection/**: Claims fraud detection and risk scoring
- **ifrs_accrual/**: IFRS 17 compliant accrual calculations
- **underwriting_scoring/**: Risk assessment and underwriting decisions
- **reinsurance_pricing/**: Reinsurance treaty pricing and optimization

**Rules:**
- ✅ Imports from core/ platform services
- ✅ Defines clear input/output contracts
- ✅ Enforces human-in-the-loop by default
- ✅ Exposes service interfaces for spaces
- ❌ NO direct model inference logic (delegates to core)
- ❌ NO UI code (that belongs in spaces)

## 📊 Datasets Layer (`datasets/`)

**Purpose**: First-class data assets with versioning, schemas, and governance.

**Structure:**
- **synthetic/**: Generated datasets for testing and development
- **benchmarks/**: Standard evaluation datasets for model performance
- **schemas/**: Data contracts and validation schemas

**Rules:**
- ✅ All datasets have documented schemas
- ✅ Version control for dataset changes
- ✅ Clear public vs. internal-only classification
- ✅ Maps to Hugging Face Datasets for distribution
- ❌ NO raw data dumps without documentation
- ❌ NO PII or sensitive data in public datasets

## 🎨 Spaces Layer (`spaces/`)

**Purpose**: Thin UI adapters that expose platform capabilities via Hugging Face Spaces.

**Available Spaces:**
- **hub_space/**: Central platform hub and navigation
- **fnol_space/**: FNOL triage demonstration
- **fraud_space/**: Fraud detection interface
- **ifrs_space/**: IFRS accrual calculator
- **underwriting_space/**: Underwriting scoring tool

**Rules (STRICTLY ENFORCED):**
- ✅ Collect user input
- ✅ Call module service interfaces
- ✅ Display results and visualizations
- ❌ NO business logic in Spaces
- ❌ NO direct model loading or inference
- ❌ NO database connections or data processing
- ❌ NO hard-coded model paths

**Example Pattern:**
```python
# spaces/fnol_space/app.py
from modules.fnol_triage.service import run_triage

def main():
    # Collect input
    claim_data = get_user_input()
    
    # Call service
    result = run_triage(claim_data)
    
    # Display output
    display_results(result)
```

## 📚 Documentation Layer (`docs/`)

**Purpose**: Architecture, governance, and compliance documentation.

**Key Documents:**
- **architecture.md**: System design, component interactions, and data flows
- **decision_boundaries.md**: Decision types, authority levels, and escalation rules
- **human_in_loop.md**: Human oversight requirements and intervention points
- **compliance.md**: Regulatory requirements and audit procedures
- **lifecycle.md**: Development workflow from PoC → MVP → Production

## 🛠️ Tools Layer (`tools/`)

**Purpose**: Development utilities, testing frameworks, and automation scripts.

**Includes:**
- Testing utilities
- Data generation scripts
- Deployment automation
- CI/CD configurations

## 🎯 What Belongs Where?

### ✅ Platform Logic (core/)
- Decision orchestration
- Policy enforcement
- Audit logging
- Security controls
- Telemetry and monitoring

### ✅ Product Logic (modules/)
- Insurance domain models
- Business rule implementations
- Service interfaces
- Input/output contracts

### ❌ NEVER in Hugging Face Spaces
- Business logic
- Model training or fine-tuning
- Data processing pipelines
- Database operations
- Authentication logic

## 🚀 Development Workflow

### Local Development
```bash
# Clone repository
git clone <repo-url>
cd bdr-insurance-platform

# Install dependencies
pip install -e .

# Run tests
pytest

# Start local development
python -m modules.fnol_triage.service
```

### Deploying to Hugging Face Spaces
```bash
# Spaces only contain UI code
# They import from the platform via pip install
cd spaces/fnol_space
huggingface-cli upload
```

## 🏗️ Architecture Principles

1. **Separation of Concerns**: Platform, products, and presentation are cleanly separated
2. **Testability**: All logic can be tested locally without external dependencies
3. **Auditability**: Every decision is logged with full context and lineage
4. **Scalability**: Designed for Docker/Kubernetes deployment
5. **Maintainability**: Clear boundaries prevent spaghetti code growth

## 🔒 Regulated Market Compliance

This platform is designed for regulated insurance markets with:
- **Audit Trails**: Immutable logs of all decisions
- **Human Oversight**: Configurable human-in-the-loop controls
- **Explainability**: Decision reasoning and evidence tracking
- **Data Governance**: Clear data lineage and access controls
- **Version Control**: All models and policies are versioned

## 👥 Team Collaboration

### For Solo Developers
- Use VS Code workspace settings for consistency
- Follow module boundaries to avoid technical debt
- Document decisions in the appropriate docs/ files

### For Teams
- Each module can be owned by a different team member
- Core platform changes require review
- Spaces can be developed independently
- Clear interfaces enable parallel development

## 📈 Scaling Path

**PoC → MVP → Production**

1. **PoC**: Develop in modules/, test locally
2. **MVP**: Deploy Spaces for stakeholder demos
3. **Production**: Containerize and deploy to Kubernetes

---

## 🚫 ARCHITECTURE FREEZE - DO / DO NOT

### ❌ DO NOT (PROHIBITED)

The following actions are **PROHIBITED** on this reference architecture:

- ❌ **Add new models** - This is a frozen architecture, not a model development platform
- ❌ **Modify decision states** - State machine is immutable
- ❌ **Change authority logic** - Authority enforcement is frozen
- ❌ **Adjust evaluation thresholds** - Evaluation criteria are locked
- ❌ **Extend Hugging Face Spaces** - HF integration is complete and frozen
- ❌ **Optimize performance** - No performance tuning allowed
- ❌ **Experiment** - This is a reference, not a sandbox
- ❌ **Refactor code** - Architecture is frozen as-is
- ❌ **Upgrade dependencies** - Dependencies are locked (requirements.lock.txt)
- ❌ **Modify governance layers** - All Phase 2 and Phase 3 components are immutable

### ✅ ALLOWED ONLY

The following actions are **ALLOWED**:

- ✅ **Fork the repository** - Create your own version for development
- ✅ **Reference the architecture** - Use as a template or guide
- ✅ **Use for advisory purposes** - Regulatory, legal, or compliance review
- ✅ **Use for educational material** - Training, documentation, or research
- ✅ **Audit and review** - External audit, compliance verification
- ✅ **Create new versions** - Fork and version as v2.0, v3.0, etc.

### 📜 Why This Freeze Exists

This reference architecture is frozen to ensure:

1. **Regulatory Stability** - Regulators can review a stable, unchanging system
2. **Audit Compliance** - Auditors can verify against a fixed baseline
3. **Legal Defensibility** - Courts can reference an immutable architecture
4. **Enterprise Standards** - Organizations can adopt a proven reference
5. **Long-Term Reference** - Future systems can compare against this baseline

### 🔐 How to Extend This Architecture

If you need to extend or modify this architecture:

1. **Fork this repository** to your own namespace
2. **Create a new version tag** (e.g., v2.0, v3.0)
3. **Document your changes** clearly in your fork
4. **Maintain this reference** as your baseline
5. **Reference this architecture** in your documentation

**Example:**
```bash
# Fork the repository
git clone https://github.com/your-org/bdr-insurance-platform.git
cd bdr-insurance-platform

# Create a new branch for your version
git checkout -b v2.0-development

# Make your changes
# ...

# Tag your new version
git tag -a v2.0 -m "Version 2.0 - Extended from reference-v1.0"
```

---

## ARCHITECTURE STATUS: FROZEN

**Reference Version:** 1.0  
**Mutability:** DISALLOWED  
**Tag:** reference-v1.0

---

## 🎯 Platform Statement (Final)

**This repository represents a reference-grade decision intelligence architecture.**

**No decision can be executed without explicit ownership, authority, evaluation, and finality enforced at runtime.**

**This system is frozen as an architectural reference and is not intended for direct feature development.**

### Governance Layers (Complete)

✅ **Phase 2.1: Ownership & Accountability Layer**  
✅ **Phase 2.1.1: Decision Authority Layer**  
✅ **Phase 2.2: Authority Anchor + Production Gate**  
✅ **Phase 2.3: Decision Finality & Execution Boundary**  
✅ **Phase 3: Evaluation Harness as Release Gate**  

### Platform Guarantees

This platform guarantees:

1. **Legal Attribution** - Every production decision is legally attributable to a specific human authority under a specific jurisdiction and mandate
2. **Runtime Enforcement** - All governance rules are enforced at runtime and cannot be bypassed
3. **Execution Boundary** - A decision can exist without execution. Execution can occur only under explicit authority and responsibility
4. **Immutable Finality** - Finality is irreversible and enforced at runtime
5. **Release Safety** - No decision logic is released, executed, or promoted unless it passes authority, responsibility, and evaluation gates

### Reference Documentation

- **Golden Reference Run:** [docs/REFERENCE_RUN_2026.md](docs/REFERENCE_RUN_2026.md)
- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **Ownership Model:** [docs/OWNERSHIP_MODEL.md](docs/OWNERSHIP_MODEL.md)
- **Decision Finality:** [docs/DECISION_FINALITY.md](docs/DECISION_FINALITY.md)
- **Phase 2.2 Summary:** [docs/PHASE_2_2_IMPLEMENTATION_SUMMARY.md](docs/PHASE_2_2_IMPLEMENTATION_SUMMARY.md)
- **Phase 3 Summary:** [PHASE_3_IMPLEMENTATION_SUMMARY.md](PHASE_3_IMPLEMENTATION_SUMMARY.md)

---

**Version:** reference-v1.0  
**Status:** FROZEN  
**Certified:** January 20, 2026  
**Owner:** Platform Architecture Team  
**Approver:** Chief Technology Officer

---

## 🚫 ARCHITECTURE FREEZE - DO / DO NOT

### ❌ DO NOT

**The following actions are PROHIBITED on this reference architecture:**

1. ❌ Add new models
2. ❌ Modify decision states
3. ❌ Change authority logic
4. ❌ Adjust evaluation thresholds
5. ❌ Extend Hugging Face Spaces
6. ❌ Optimize performance
7. ❌ Experiment with new features
8. ❌ Refactor code
9. ❌ Upgrade dependencies
10. ❌ Modify governance layers

### ✅ ALLOWED ONLY

**The following actions are PERMITTED:**

1. ✅ Fork the repository
2. ✅ Reference the architecture
3. ✅ Use for advisory purposes
4. ✅ Use for regulatory review
5. ✅ Use for educational material
6. ✅ Create new versions (with proper versioning)

### 📋 Freeze Rationale

This architecture is frozen to ensure:

1. **Regulatory Stability** - Regulators can review a stable, unchanging system
2. **Audit Compliance** - Auditors can verify against a fixed baseline
3. **Legal Defensibility** - Courts can reference an immutable architecture
4. **Enterprise Standards** - Organizations can adopt a proven reference
5. **Long-term Reference** - Future systems can compare against this baseline

### 🔄 Extension Guidance

If you need to extend or modify this architecture:

1. **Fork** this repository to a new namespace
2. **Create a new version** (e.g., v2.0, v3.0)
3. **Document changes** clearly in your fork
4. **Maintain this reference** as the baseline
5. **Reference this architecture** in your documentation

---

## 🤝 Contributing

See individual module READMEs for contribution guidelines.

## 📄 License

[Specify License]

## 📞 Contact

For questions or support, contact the BDR platform team.

---

**Built for Enterprise Adoption | Designed for Regulated AI | Ready for Long-term Maintenance**
