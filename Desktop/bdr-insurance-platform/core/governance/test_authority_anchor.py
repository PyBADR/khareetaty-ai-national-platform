"""Test examples for Authority Anchor enforcement.

Demonstrates:
1. PASSING example: Valid authority with anchor
2. FAILING example: Missing anchor in production (BLOCKED)
3. FAILING example: Expired anchor (BLOCKED)
4. FAILING example: Jurisdiction mismatch (BLOCKED)
"""

from datetime import datetime, timezone, timedelta
from core.governance.authority_anchor import (
    AuthorityAnchor,
    Jurisdiction,
    create_authority_anchor,
    validate_anchor_for_production,
    create_authority_explanation,
)
from core.governance.enforcement import (
    enforce_authority_anchor,
    AuthorityAnchorViolation,
    get_anchor_audit_metadata,
)
from core.governance.authority import DecisionAuthority, DecisionSeverity
from core.decision_engine.enums import DecisionType


def test_passing_example_valid_anchor():
    """PASSING: Valid authority with anchor in production."""
    print("\n" + "="*80)
    print("TEST 1: PASSING - Valid Authority with Anchor")
    print("="*80)
    
    # Create valid anchor
    anchor = create_authority_anchor(
        legal_entity="GIG Takaful Kuwait",
        jurisdiction=Jurisdiction.KW,
        job_title="Senior Claims Manager",
        contract_reference="EMP-2024-KW-CM-001",
        valid_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2027, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        metadata={"department": "Claims", "max_claim_amount": 50000}
    )
    
    # Create authority with anchor
    authority = DecisionAuthority(
        authority_id="auth_kw_claims_001",
        role="Senior Claims Manager",
        can_execute=True,
        can_override=True,
        can_finalize=False,
        requires_human_signature=True,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ELEVATED,
        allowed_decision_types={DecisionType.BOUNDED, DecisionType.ADVISORY},
        authority_anchor=anchor
    )
    
    # Test enforcement in production
    try:
        enforce_authority_anchor(
            authority=authority,
            environment="production",
            required_jurisdiction=Jurisdiction.KW
        )
        print("✅ PASSED: Authority anchor validation successful")
        print(f"   Legal Entity: {anchor.legal_entity}")
        print(f"   Jurisdiction: {anchor.jurisdiction.value}")
        print(f"   Job Title: {anchor.job_title}")
        print(f"   Contract: {anchor.contract_reference}")
        print(f"   Valid: {anchor.is_currently_valid()}")
        
        # Get audit metadata
        audit_meta = get_anchor_audit_metadata(authority)
        print(f"\n   Audit Metadata:")
        print(f"   - Has Anchor: {audit_meta['has_anchor']}")
        print(f"   - Days Until Expiry: {audit_meta['days_until_expiry']}")
        
        # Create explanation
        explanation = create_authority_explanation(
            allowed=True,
            reason=f"Authority validated: {anchor.job_title} at {anchor.legal_entity} under {anchor.jurisdiction.value} jurisdiction",
            governing_policy="Production Authority Anchor Policy - Phase 2.2",
            anchor=anchor
        )
        print(f"\n   Explanation: {explanation.why_allowed}")
        
        return True
        
    except AuthorityAnchorViolation as e:
        print(f"❌ FAILED: {e}")
        return False


def test_failing_example_missing_anchor():
    """FAILING: Missing anchor in production (BLOCKED)."""
    print("\n" + "="*80)
    print("TEST 2: FAILING - Missing Anchor in Production (BLOCKED)")
    print("="*80)
    
    # Create authority WITHOUT anchor
    authority = DecisionAuthority(
        authority_id="auth_no_anchor_001",
        role="Claims Manager",
        can_execute=True,
        can_override=False,
        can_finalize=False,
        requires_human_signature=True,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ROUTINE,
        allowed_decision_types={DecisionType.BOUNDED},
        authority_anchor=None  # NO ANCHOR
    )
    
    # Test enforcement in production
    try:
        enforce_authority_anchor(
            authority=authority,
            environment="production"
        )
        print("❌ UNEXPECTED: Should have been blocked")
        return False
        
    except AuthorityAnchorViolation as e:
        print(f"✅ CORRECTLY BLOCKED: {e}")
        print("\n   This is the expected behavior in production.")
        print("   All production decisions MUST have legal attribution.")
        
        # Create explanation for blocking
        explanation = create_authority_explanation(
            allowed=False,
            reason=str(e),
            governing_policy="Production Authority Anchor Policy - Phase 2.2",
            anchor=None
        )
        print(f"\n   Blocking Reason: {explanation.why_blocked}")
        
        return True


def test_failing_example_expired_anchor():
    """FAILING: Expired anchor (BLOCKED)."""
    print("\n" + "="*80)
    print("TEST 3: FAILING - Expired Anchor (BLOCKED)")
    print("="*80)
    
    # Create EXPIRED anchor
    anchor = create_authority_anchor(
        legal_entity="GIG Takaful Kuwait",
        jurisdiction=Jurisdiction.KW,
        job_title="Former Claims Manager",
        contract_reference="EMP-2023-KW-CM-EXPIRED",
        valid_from=datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),  # EXPIRED
        metadata={"status": "expired"}
    )
    
    # Create authority with expired anchor
    authority = DecisionAuthority(
        authority_id="auth_expired_001",
        role="Former Claims Manager",
        can_execute=True,
        can_override=False,
        can_finalize=False,
        requires_human_signature=True,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ROUTINE,
        allowed_decision_types={DecisionType.BOUNDED},
        authority_anchor=anchor
    )
    
    # Test enforcement in production
    try:
        enforce_authority_anchor(
            authority=authority,
            environment="production"
        )
        print("❌ UNEXPECTED: Should have been blocked")
        return False
        
    except AuthorityAnchorViolation as e:
        print(f"✅ CORRECTLY BLOCKED: {e}")
        print(f"\n   Anchor expired at: {anchor.valid_until.isoformat()}")
        print(f"   Current time: {datetime.now(timezone.utc).isoformat()}")
        print("   Expired authorities cannot make production decisions.")
        
        return True


def test_failing_example_jurisdiction_mismatch():
    """FAILING: Jurisdiction mismatch (BLOCKED)."""
    print("\n" + "="*80)
    print("TEST 4: FAILING - Jurisdiction Mismatch (BLOCKED)")
    print("="*80)
    
    # Create anchor for Kuwait
    anchor = create_authority_anchor(
        legal_entity="GIG Takaful Kuwait",
        jurisdiction=Jurisdiction.KW,  # Kuwait
        job_title="Claims Manager",
        contract_reference="EMP-2024-KW-CM-001",
        valid_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        valid_until=datetime(2027, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
    )
    
    # Create authority
    authority = DecisionAuthority(
        authority_id="auth_kw_001",
        role="Claims Manager",
        can_execute=True,
        can_override=False,
        can_finalize=False,
        requires_human_signature=True,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ROUTINE,
        allowed_decision_types={DecisionType.BOUNDED},
        authority_anchor=anchor
    )
    
    # Test enforcement with DIFFERENT jurisdiction requirement
    try:
        enforce_authority_anchor(
            authority=authority,
            environment="production",
            required_jurisdiction=Jurisdiction.SA  # Require Saudi Arabia
        )
        print("❌ UNEXPECTED: Should have been blocked")
        return False
        
    except AuthorityAnchorViolation as e:
        print(f"✅ CORRECTLY BLOCKED: {e}")
        print(f"\n   Anchor jurisdiction: {anchor.jurisdiction.value}")
        print(f"   Required jurisdiction: SA")
        print("   Cross-jurisdiction decisions require proper authority.")
        
        return True


def test_development_mode_warning():
    """Development mode: Warning but not blocked."""
    print("\n" + "="*80)
    print("TEST 5: Development Mode - Warning Only (Not Blocked)")
    print("="*80)
    
    # Create authority WITHOUT anchor
    authority = DecisionAuthority(
        authority_id="auth_dev_001",
        role="Developer",
        can_execute=True,
        can_override=False,
        can_finalize=False,
        requires_human_signature=False,
        requires_committee=False,
        max_decision_severity=DecisionSeverity.ROUTINE,
        allowed_decision_types={DecisionType.SIMULATION},
        authority_anchor=None  # NO ANCHOR
    )
    
    # Test enforcement in DEVELOPMENT
    try:
        enforce_authority_anchor(
            authority=authority,
            environment="development"  # DEV mode
        )
        print("✅ ALLOWED in development (with warning)")
        print("   Development mode allows missing anchors for testing.")
        print("   This would be BLOCKED in production.")
        
        return True
        
    except AuthorityAnchorViolation as e:
        print(f"❌ UNEXPECTED: Should not block in development: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# AUTHORITY ANCHOR ENFORCEMENT TESTS")
    print("# Phase 2.2: Legally Attributable Decision Execution")
    print("#"*80)
    
    results = []
    
    # Run tests
    results.append(("Valid Anchor", test_passing_example_valid_anchor()))
    results.append(("Missing Anchor", test_failing_example_missing_anchor()))
    results.append(("Expired Anchor", test_failing_example_expired_anchor()))
    results.append(("Jurisdiction Mismatch", test_failing_example_jurisdiction_mismatch()))
    results.append(("Development Mode", test_development_mode_warning()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("\nAuthority Anchor enforcement is working correctly:")
        print("- Production decisions require valid anchors")
        print("- Expired anchors are blocked")
        print("- Jurisdiction mismatches are blocked")
        print("- Development mode allows testing without anchors")
        print("\nEvery production decision is now legally attributable.")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*80)
