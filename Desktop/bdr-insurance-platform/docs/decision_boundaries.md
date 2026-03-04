# Decision Boundaries & Authority Levels

**Version:** 1.0  
**Last Updated:** January 2026  
**Purpose:** Define decision types, authority levels, and escalation rules

---

## 1. Overview

In regulated insurance markets, not all decisions can be fully automated. This document defines clear boundaries between automated, human-assisted, and human-only decisions, ensuring compliance while maximizing efficiency.

**Core Principle:** *Every decision has a defined authority level and escalation path.*

---

## 2. Decision Type Taxonomy

### 2.1 Decision Type Definitions

| Decision Type | Description | Automation Level | Human Role |
|--------------|-------------|------------------|------------|
| **ADVISORY** | System provides recommendations, human decides | Low | Decision Maker |
| **BOUNDED** | Automated within constraints, escalates exceptions | High | Exception Handler |
| **SIMULATION** | What-if analysis, no real-world impact | N/A | Analyst |
| **HUMAN_ONLY** | Requires human judgment, no automation | None | Decision Maker |

### 2.2 Decision Type Selection Matrix

```
                    High Risk
                        ↑
                        │
        HUMAN_ONLY      │      ADVISORY
                        │
    ────────────────────┼────────────────────→
                        │         High Complexity
        BOUNDED         │      SIMULATION
                        │
                    Low Risk
```

**Selection Criteria:**

1. **Risk Level**
   - Financial impact
   - Regulatory implications
   - Reputational risk
   - Customer impact

2. **Complexity**
   - Number of variables
   - Uncertainty level
   - Precedent availability
   - Stakeholder count

3. **Regulatory Requirements**
   - Explicit human oversight mandates
   - Audit trail requirements
   - Explainability needs

---

## 3. Authority Levels

### 3.1 Authority Hierarchy

```
Level 4: Executive
    ↑
    │ Escalation Path
    ↓
Level 3: Manager
    ↑
    │
    ↓
Level 2: Supervisor
    ↑
    │
    ↓
Level 1: Automated System
```

### 3.2 Authority Level Definitions

#### Level 1: Automated System
**Scope:** Routine, low-risk decisions within established parameters

**Examples:**
- Standard FNOL triage (severity < 5)
- Fraud screening (clear negative)
- Policy renewals (no changes)

**Constraints:**
- Must operate within policy bounds
- Confidence threshold ≥ 0.85
- No regulatory flags
- Financial impact < $10,000

**Escalation Triggers:**
- Confidence < 0.85
- Policy violation detected
- Unusual pattern detected
- Financial impact ≥ $10,000

#### Level 2: Supervisor
**Scope:** Moderate-risk decisions, exceptions from Level 1

**Examples:**
- FNOL triage (severity 5-7)
- Fraud cases (moderate suspicion)
- Underwriting exceptions
- Claims adjustments ($10K-$50K)

**Authority:**
- Approve/reject Level 1 escalations
- Override system recommendations (with justification)
- Modify decision parameters within limits

**Escalation Triggers:**
- Financial impact ≥ $50,000
- Regulatory compliance concerns
- Novel case without precedent
- Customer complaint escalation

#### Level 3: Manager
**Scope:** High-risk decisions, strategic exceptions

**Examples:**
- Large claims ($50K-$250K)
- Policy exceptions
- Fraud prosecution decisions
- Reinsurance treaty adjustments

**Authority:**
- Approve/reject Level 2 escalations
- Modify policies within governance framework
- Authorize special investigations
- Sign off on regulatory submissions

**Escalation Triggers:**
- Financial impact ≥ $250,000
- Legal implications
- Regulatory inquiry
- Reputational risk

#### Level 4: Executive
**Scope:** Critical decisions, strategic direction

**Examples:**
- Claims > $250K
- Major policy changes
- Regulatory settlements
- Strategic partnerships

**Authority:**
- Final decision authority
- Policy framework changes
- Regulatory negotiations
- Public statements

---

## 4. Decision Boundaries by Module

### 4.1 FNOL Triage

#### Automated (Level 1)
**Conditions:**
- Severity score 1-4
- Standard claim types
- Complete information
- No fraud indicators

**Output:**
- Priority assignment
- Adjuster routing
- Initial reserve estimate

**Boundaries:**
- Reserve estimate ≤ $10,000
- Standard processing time
- No special handling required

#### Requires Approval (Level 2+)
**Triggers:**
- Severity score ≥ 5
- Incomplete information
- Fraud indicators present
- Reserve estimate > $10,000
- Multiple claimants
- Legal representation mentioned

### 4.2 Fraud Detection

#### Automated (Level 1)
**Conditions:**
- Clear negative (fraud score < 0.3)
- Standard patterns
- No historical flags

**Output:**
- Pass to normal processing
- No investigation required

**Boundaries:**
- Fraud score < 0.3
- No prior fraud history
- Claim amount < $25,000

#### Requires Investigation (Level 2)
**Triggers:**
- Fraud score 0.3-0.7
- Suspicious patterns detected
- Prior fraud history
- Claim amount $25K-$100K

**Actions:**
- Assign to fraud investigator
- Request additional documentation
- Delay payment pending review

#### Requires Prosecution Review (Level 3)
**Triggers:**
- Fraud score > 0.7
- Clear evidence of fraud
- Claim amount > $100K
- Organized fraud ring suspected

### 4.3 IFRS 17 Accrual

#### Automated (Level 1)
**Conditions:**
- Standard contract types
- Complete data available
- No material changes
- Quarterly calculations

**Output:**
- Accrual amounts
- Liability estimates
- Disclosure notes

**Boundaries:**
- Standard contract terms
- Historical data available
- No significant events

#### Requires Review (Level 2)
**Triggers:**
- New contract types
- Material changes in assumptions
- Significant events (M&A, regulatory changes)
- Annual reporting

#### Requires Actuarial Sign-off (Level 3)
**Triggers:**
- External audit
- Regulatory filing
- Material restatements
- Assumption changes > 10%

### 4.4 Underwriting Scoring

#### Automated (Level 1)
**Conditions:**
- Standard risk profiles
- Complete application
- Score within normal range
- Premium < $50,000

**Output:**
- Accept/Decline/Refer
- Premium quote
- Terms and conditions

**Boundaries:**
- Risk score within 2 std dev
- No unusual risk factors
- Standard coverage amounts

#### Requires Underwriter Review (Level 2)
**Triggers:**
- Risk score outside normal range
- Unusual risk factors
- Premium $50K-$250K
- Non-standard coverage requests

#### Requires Senior Underwriter (Level 3)
**Triggers:**
- High-risk accounts
- Premium > $250K
- Complex risk structures
- Reinsurance required

### 4.5 Reinsurance Pricing

#### Automated (Level 1)
**Conditions:**
- Standard treaty types
- Historical data available
- No market disruptions
- Renewal pricing

**Output:**
- Price recommendations
- Risk transfer analysis
- Capacity suggestions

**Boundaries:**
- Treaty premium < $10M
- Standard terms
- Established relationships

#### Requires Pricing Actuary (Level 2)
**Triggers:**
- New treaty structures
- Premium $10M-$50M
- Market volatility
- Non-standard terms

#### Requires Executive Approval (Level 3+)
**Triggers:**
- Premium > $50M
- Novel risk transfer structures
- Strategic partnerships
- Regulatory implications

---

## 5. Escalation Rules

### 5.1 Automatic Escalation

**System automatically escalates when:**

1. **Confidence Threshold**
   - Decision confidence < 0.85
   - High variance in model predictions
   - Conflicting policy rules

2. **Financial Thresholds**
   - Amount exceeds authority level
   - Cumulative exposure limits reached
   - Reserve adequacy concerns

3. **Regulatory Flags**
   - Compliance violation detected
   - Reportable event triggered
   - Audit trail gaps

4. **Risk Indicators**
   - Fraud score above threshold
   - Unusual pattern detected
   - External risk factors

5. **Data Quality Issues**
   - Missing critical information
   - Inconsistent data
   - Stale data (> 90 days)

### 5.2 Manual Escalation

**Users can escalate when:**

1. **Professional Judgment**
   - Situation requires expertise
   - Novel circumstances
   - Ethical concerns

2. **Customer Request**
   - Customer disputes decision
   - Requests human review
   - Complaint filed

3. **Stakeholder Concerns**
   - Internal audit questions
   - Regulatory inquiry
   - Legal review needed

### 5.3 Escalation Process

```
Decision Requires Escalation
    ↓
System Creates Escalation Ticket
    ↓
Assigns to Next Authority Level
    ↓
Notification Sent (Email/SMS)
    ↓
Reviewer Accesses Full Context
    ↓
Reviewer Makes Decision
    ↓
Decision Logged in Audit Trail
    ↓
Original Requestor Notified
```

**Escalation SLAs:**

| Priority | Response Time | Resolution Time |
|----------|--------------|-----------------|
| Critical | 1 hour | 4 hours |
| High | 4 hours | 24 hours |
| Medium | 24 hours | 3 days |
| Low | 3 days | 7 days |

---

## 6. Override Mechanisms

### 6.1 Override Authority

**Who can override system decisions:**

| Authority Level | Override Scope | Justification Required |
|----------------|----------------|------------------------|
| Supervisor | Level 1 decisions | Yes |
| Manager | Level 1-2 decisions | Yes |
| Executive | Any decision | Yes |

### 6.2 Override Process

1. **Request Override**
   - State reason for override
   - Provide supporting evidence
   - Specify alternative decision

2. **Review Override Request**
   - System checks authority level
   - Validates justification
   - Logs override attempt

3. **Approve/Deny Override**
   - Authorized user reviews
   - Makes final decision
   - Documents reasoning

4. **Audit Override**
   - All overrides logged
   - Periodic review by compliance
   - Pattern analysis for policy updates

### 6.3 Override Monitoring

**Red Flags:**
- High override rate (> 10%)
- Consistent overrides by same user
- Overrides without proper justification
- Overrides that result in losses

**Actions:**
- Quarterly override review
- Retraining if needed
- Policy adjustments
- System improvements

---

## 7. Confidence Thresholds

### 7.1 Threshold Calibration

| Decision Type | Minimum Confidence | Escalation Threshold |
|--------------|-------------------|---------------------|
| ADVISORY | 0.70 | 0.85 |
| BOUNDED | 0.85 | 0.90 |
| SIMULATION | 0.60 | N/A |

### 7.2 Confidence Calculation

**Factors in confidence score:**

1. **Model Confidence**
   - Prediction probability
   - Model uncertainty
   - Ensemble agreement

2. **Data Quality**
   - Completeness
   - Freshness
   - Consistency

3. **Historical Performance**
   - Similar case outcomes
   - Model accuracy on similar cases
   - Override rate

4. **External Factors**
   - Market conditions
   - Regulatory changes
   - Seasonal patterns

**Formula:**
```
Final Confidence = (
    0.4 × Model Confidence +
    0.3 × Data Quality Score +
    0.2 × Historical Performance +
    0.1 × External Factor Adjustment
)
```

---

## 8. Boundary Adjustments

### 8.1 When to Adjust Boundaries

**Triggers for boundary review:**

1. **Performance Metrics**
   - High escalation rate (> 20%)
   - Low automation rate (< 60%)
   - Poor decision accuracy (< 90%)

2. **Regulatory Changes**
   - New compliance requirements
   - Industry guidance updates
   - Audit findings

3. **Business Changes**
   - New products launched
   - Market expansion
   - Risk appetite changes

4. **Technology Improvements**
   - Better models available
   - Enhanced data sources
   - Improved explainability

### 8.2 Boundary Adjustment Process

1. **Proposal**
   - Document current boundaries
   - Propose changes with rationale
   - Estimate impact

2. **Analysis**
   - Simulate with historical data
   - Assess risk implications
   - Calculate cost/benefit

3. **Approval**
   - Manager review
   - Compliance sign-off
   - Executive approval (if material)

4. **Implementation**
   - Update system configuration
   - Train affected users
   - Monitor closely (30 days)

5. **Review**
   - Assess impact after 90 days
   - Adjust if needed
   - Document lessons learned

---

## 9. Compliance & Audit

### 9.1 Audit Trail Requirements

**Every decision must log:**
- Decision type and authority level
- Input data (sanitized)
- System recommendation
- Final decision
- Decision maker (human or system)
- Confidence score
- Escalation path (if any)
- Override details (if any)
- Timestamp and trace ID

### 9.2 Periodic Reviews

**Quarterly:**
- Decision accuracy by type
- Escalation rate analysis
- Override pattern review
- Boundary effectiveness

**Annually:**
- Comprehensive audit
- Regulatory compliance check
- Boundary recalibration
- Policy updates

---

## 10. Examples

### 10.1 Example: FNOL Triage Decision

**Scenario:** Auto accident claim

**Input:**
- Severity: 6
- Injuries: Minor
- Property damage: $15,000
- Claimant: No prior claims

**Decision Flow:**

1. **System Analysis**
   - Severity score: 6 (moderate)
   - Fraud score: 0.15 (low)
   - Confidence: 0.82

2. **Boundary Check**
   - Severity ≥ 5 → Requires Level 2
   - Confidence < 0.85 → Requires Level 2
   - Property damage > $10K → Requires Level 2

3. **Escalation**
   - System escalates to Supervisor
   - Provides recommendation: "Standard priority, assign to adjuster team B"
   - Flags: "Moderate severity, slightly below confidence threshold"

4. **Supervisor Review**
   - Reviews system analysis
   - Checks claimant history
   - Approves recommendation
   - Adds note: "Standard processing, no special handling"

5. **Outcome**
   - Decision: Approved
   - Authority: Level 2 (Supervisor)
   - Processing time: 2 hours
   - Logged in audit trail

### 10.2 Example: Fraud Detection Decision

**Scenario:** Suspicious claim pattern

**Input:**
- Claim amount: $45,000
- Fraud score: 0.72
- Prior claims: 3 in 18 months
- Documentation: Incomplete

**Decision Flow:**

1. **System Analysis**
   - Fraud score: 0.72 (high)
   - Pattern: Multiple claims, short timeframe
   - Confidence: 0.88

2. **Boundary Check**
   - Fraud score > 0.7 → Requires Level 3
   - Amount > $25K → Requires Level 2
   - Incomplete docs → Requires investigation

3. **Escalation**
   - System escalates to Manager (Level 3)
   - Assigns to fraud investigation unit
   - Flags: "High fraud probability, prosecution review recommended"

4. **Manager Review**
   - Reviews fraud indicators
   - Requests full investigation
   - Holds payment pending investigation
   - Considers prosecution referral

5. **Outcome**
   - Decision: Investigation initiated
   - Authority: Level 3 (Manager)
   - Payment: Held
   - Investigation: 30-day timeline
   - Logged in audit trail with fraud flag

---

## 11. Conclusion

Clear decision boundaries ensure:
- **Efficiency**: Automate routine decisions
- **Safety**: Human oversight for high-risk decisions
- **Compliance**: Meet regulatory requirements
- **Auditability**: Complete decision trail
- **Adaptability**: Boundaries adjust with experience

**Key Principles:**
1. Every decision has a defined authority level
2. Escalation is automatic when boundaries are exceeded
3. All decisions are auditable
4. Boundaries are reviewed and adjusted regularly
5. Human judgment is valued and preserved

---

**Document Maintenance:**
- Review quarterly
- Update after regulatory changes
- Adjust based on performance data
- Version control in Git
