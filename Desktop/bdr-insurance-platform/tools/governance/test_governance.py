"""Pytest tests for Ownership & Accountability Layer.

Tests the governance module to ensure:
- Ownership primitives work correctly
- Accountability scopes are enforced
- Runtime enforcement blocks violations
- No anonymous owners allowed
- Audit metadata includes ownership
"""

import pytest
from datetime import datetime
from decimal import Decimal

from core.governance import (
    DecisionOwner,
    AccountabilityChain,
    AccountabilityScope,
    ImpactLevel,
    RegulatoryClass,
    OwnershipViolation,
    AccountabilityViolation,
    enforce_ownership,
    validate_ownership_chain,
    create_system_ownership,
    create_human_ownership,
    get_scope_for_decision_type,
    ADVISORY_SCOPE,
    BOUNDED_LOW_SCOPE,
    BOUNDED_MEDIUM_SCOPE,
    BOUNDED_HIGH_SCOPE,
    SIMULATION_SCOPE,
)

from core.decision_engine import (
    DecisionRequest,
    DecisionTypeEnum,
)


class TestDecisionOwner:
    """Test DecisionOwner immutable primitive."""
    
    def test_valid_owner_creation(self):
        """Test creating a valid decision owner."""
        owner = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        assert owner.owner_id == "emp_12345"
        assert owner.owner_type == "human"
        assert owner.organization == "gig_takaful_kuwait"
        assert owner.role == "claims_manager"
    
    def test_owner_is_frozen(self):
        """Test that DecisionOwner is immutable."""
        owner = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            owner.owner_id = "emp_99999"
    
    def test_anonymous_owner_rejected(self):
        """Test that anonymous owners are rejected."""
        with pytest.raises(ValueError, match="anonymous owners are forbidden"):
            DecisionOwner(
                owner_id="anonymous",
                owner_type="human",
                organization="gig_takaful_kuwait",
                role="claims_manager",
            )
    
    def test_empty_owner_id_rejected(self):
        """Test that empty owner_id is rejected."""
        with pytest.raises(ValueError, match="owner_id cannot be empty"):
            DecisionOwner(
                owner_id="",
                owner_type="human",
                organization="gig_takaful_kuwait",
                role="claims_manager",
            )
    
    def test_generic_owner_ids_rejected(self):
        """Test that generic owner IDs are rejected."""
        generic_ids = ["unknown", "system", "auto"]
        
        for generic_id in generic_ids:
            with pytest.raises(ValueError, match="too generic"):
                DecisionOwner(
                    owner_id=generic_id,
                    owner_type="human",
                    organization="gig_takaful_kuwait",
                    role="claims_manager",
                )
    
    def test_owner_to_dict(self):
        """Test converting owner to dictionary."""
        owner = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        owner_dict = owner.to_dict()
        
        assert owner_dict["owner_id"] == "emp_12345"
        assert owner_dict["owner_type"] == "human"
        assert owner_dict["organization"] == "gig_takaful_kuwait"
        assert owner_dict["role"] == "claims_manager"


class TestAccountabilityChain:
    """Test AccountabilityChain immutable primitive."""
    
    def test_valid_chain_creation(self):
        """Test creating a valid accountability chain."""
        primary = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        escalation = DecisionOwner(
            owner_id="emp_67890",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="senior_claims_manager",
        )
        
        ultimate = DecisionOwner(
            owner_id="committee_claims",
            owner_type="committee",
            organization="gig_takaful_kuwait",
            role="claims_committee",
        )
        
        chain = AccountabilityChain(
            primary_owner=primary,
            escalation_owner=escalation,
            ultimate_accountable=ultimate,
            override_authority="human_only",
            liability_scope="advisory",
        )
        
        assert chain.primary_owner == primary
        assert chain.escalation_owner == escalation
        assert chain.ultimate_accountable == ultimate
        assert chain.created_at is not None
    
    def test_self_escalation_rejected(self):
        """Test that self-escalation is rejected."""
        primary = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        ultimate = DecisionOwner(
            owner_id="committee_claims",
            owner_type="committee",
            organization="gig_takaful_kuwait",
            role="claims_committee",
        )
        
        with pytest.raises(ValueError, match="cannot be the same"):
            AccountabilityChain(
                primary_owner=primary,
                escalation_owner=primary,  # Same as primary!
                ultimate_accountable=ultimate,
                override_authority="human_only",
                liability_scope="advisory",
            )
    
    def test_system_ultimate_accountable_rejected(self):
        """Test that system cannot be ultimate accountable."""
        primary = DecisionOwner(
            owner_id="emp_12345",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        escalation = DecisionOwner(
            owner_id="emp_67890",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="senior_claims_manager",
        )
        
        system_ultimate = DecisionOwner(
            owner_id="system_ai",
            owner_type="system",
            organization="gig_takaful_kuwait",
            role="ai_system",
        )
        
        with pytest.raises(ValueError, match="must be a human or committee"):
            AccountabilityChain(
                primary_owner=primary,
                escalation_owner=escalation,
                ultimate_accountable=system_ultimate,  # System not allowed!
                override_authority="human_only",
                liability_scope="advisory",
            )
    
    def test_automated_action_requires_human_override(self):
        """Test that automated_action liability requires human override."""
        primary = DecisionOwner(
            owner_id="system_fnol",
            owner_type="system",
            organization="gig_takaful_kuwait",
            role="fnol_triage_system",
        )
        
        escalation = DecisionOwner(
            owner_id="emp_67890",
            owner_type="human",
            organization="gig_takaful_kuwait",
            role="claims_manager",
        )
        
        ultimate = DecisionOwner(
            owner_id="committee_claims",
            owner_type="committee",
            organization="gig_takaful_kuwait",
            role="claims_committee",
        )
        
        with pytest.raises(ValueError, match="automated_action liability requires"):
            AccountabilityChain(
                primary_owner=primary,
                escalation_owner=escalation,
                ultimate_accountable=ultimate,
                override_authority="system_allowed",  # Not allowed for automated_action!
                liability_scope="automated_action",
            )


class TestAccountabilityScope:
    """Test AccountabilityScope enforcement."""
    
    def test_advisory_scope(self):
        """Test advisory scope configuration."""
        assert ADVISORY_SCOPE.decision_type == DecisionTypeEnum.ADVISORY
        assert "auto_approve" in ADVISORY_SCOPE.forbidden_actions
        assert "provide_recommendation" in ADVISORY_SCOPE.allowed_actions
    
    def test_bounded_low_scope(self):
        """Test bounded low scope configuration."""
        assert BOUNDED_LOW_SCOPE.decision_type == DecisionTypeEnum.BOUNDED
        assert BOUNDED_LOW_SCOPE.max_financial_exposure == 1000.0
        assert BOUNDED_LOW_SCOPE.max_impact_level == ImpactLevel.LOW
    
    def test_financial_exposure_validation(self):
        """Test financial exposure validation."""
        # Within limit
        is_valid, reason = BOUNDED_LOW_SCOPE.validate_financial_exposure(500.0)
        assert is_valid
        assert reason is None
        
        # Exceeds limit
        is_valid, reason = BOUNDED_LOW_SCOPE.validate_financial_exposure(5000.0)
        assert not is_valid
        assert "exceeds maximum" in reason
    
    def test_action_allowed(self):
        """Test action allowed checking."""
        assert BOUNDED_LOW_SCOPE.is_action_allowed("auto_approve")
        assert not BOUNDED_LOW_SCOPE.is_action_allowed("disburse_funds")
        assert not BOUNDED_LOW_SCOPE.is_action_allowed("unknown_action")
    
    def test_simulation_zero_financial_exposure(self):
        """Test that simulation scope has zero financial exposure."""
        assert SIMULATION_SCOPE.max_financial_exposure == 0.0
        
        # Should fail validation for non-zero exposure
        is_valid, reason = SIMULATION_SCOPE.validate_financial_exposure(100.0)
        assert not is_valid


class TestRuntimeEnforcement:
    """Test runtime enforcement of ownership."""
    
    def test_enforce_ownership_missing_ownership(self):
        """Test that missing ownership raises OwnershipViolation."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
        )
        
        with pytest.raises(OwnershipViolation, match="has no ownership"):
            enforce_ownership(
                decision_request=request,
                ownership=None,  # Missing!
                scope=BOUNDED_LOW_SCOPE,
            )
    
    def test_enforce_ownership_missing_scope(self):
        """Test that missing scope raises AccountabilityViolation."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
        )
        
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        with pytest.raises(AccountabilityViolation, match="has no accountability scope"):
            enforce_ownership(
                decision_request=request,
                ownership=ownership,
                scope=None,  # Missing!
            )
    
    def test_enforce_ownership_type_mismatch(self):
        """Test that decision type mismatch raises AccountabilityViolation."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.ADVISORY,  # Advisory
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
        )
        
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        with pytest.raises(AccountabilityViolation, match="Decision type mismatch"):
            enforce_ownership(
                decision_request=request,
                ownership=ownership,
                scope=BOUNDED_LOW_SCOPE,  # Bounded scope, but request is Advisory!
            )
    
    def test_enforce_ownership_financial_exposure_exceeded(self):
        """Test that exceeding financial exposure raises AccountabilityViolation."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 50000.0},  # Exceeds LOW scope limit!
            user_id="user_123",
        )
        
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        with pytest.raises(AccountabilityViolation, match="Financial exposure violation"):
            enforce_ownership(
                decision_request=request,
                ownership=ownership,
                scope=BOUNDED_LOW_SCOPE,
            )
    
    def test_enforce_ownership_forbidden_action(self):
        """Test that forbidden actions raise AccountabilityViolation."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={
                "claim_amount": 500.0,
                "requested_action": "disburse_funds",  # Forbidden!
            },
            user_id="user_123",
        )
        
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        with pytest.raises(AccountabilityViolation, match="Forbidden action"):
            enforce_ownership(
                decision_request=request,
                ownership=ownership,
                scope=BOUNDED_LOW_SCOPE,
            )
    
    def test_enforce_ownership_valid(self):
        """Test that valid ownership passes enforcement."""
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
        )
        
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        # Should not raise
        enforce_ownership(
            decision_request=request,
            ownership=ownership,
            scope=BOUNDED_LOW_SCOPE,
        )


class TestHelperFunctions:
    """Test helper functions for creating ownership."""
    
    def test_create_system_ownership(self):
        """Test creating system ownership."""
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        assert ownership.primary_owner.owner_type == "system"
        assert ownership.escalation_owner.owner_type == "human"
        assert ownership.ultimate_accountable.owner_type == "human"
    
    def test_create_human_ownership(self):
        """Test creating human ownership."""
        ownership = create_human_ownership(
            human_id="emp_12345",
            role="claims_manager",
            organization="gig_takaful_kuwait",
            supervisor_id="emp_67890",
            supervisor_role="senior_claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        assert ownership.primary_owner.owner_type == "human"
        assert ownership.escalation_owner.owner_type == "human"
        assert ownership.ultimate_accountable.owner_type == "human"
    
    def test_get_scope_for_decision_type(self):
        """Test getting scope for decision type."""
        # Advisory
        scope = get_scope_for_decision_type(DecisionTypeEnum.ADVISORY)
        assert scope == ADVISORY_SCOPE
        
        # Simulation
        scope = get_scope_for_decision_type(DecisionTypeEnum.SIMULATION)
        assert scope == SIMULATION_SCOPE
        
        # Bounded - low
        scope = get_scope_for_decision_type(DecisionTypeEnum.BOUNDED, financial_exposure=500.0)
        assert scope == BOUNDED_LOW_SCOPE
        
        # Bounded - medium
        scope = get_scope_for_decision_type(DecisionTypeEnum.BOUNDED, financial_exposure=25000.0)
        assert scope == BOUNDED_MEDIUM_SCOPE
        
        # Bounded - high
        scope = get_scope_for_decision_type(DecisionTypeEnum.BOUNDED, financial_exposure=100000.0)
        assert scope == BOUNDED_HIGH_SCOPE


class TestDecisionRequestIntegration:
    """Test DecisionRequest integration with ownership."""
    
    def test_decision_request_with_ownership(self):
        """Test creating DecisionRequest with ownership."""
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
            ownership=ownership,
            accountability_scope=BOUNDED_LOW_SCOPE,
        )
        
        assert request.ownership == ownership
        assert request.accountability_scope == BOUNDED_LOW_SCOPE
    
    def test_decision_request_enforce_ownership(self):
        """Test enforcing ownership on DecisionRequest."""
        ownership = create_system_ownership(
            system_id="fnol_triage_v1",
            organization="gig_takaful_kuwait",
            human_supervisor_id="emp_12345",
            human_supervisor_role="claims_manager",
            ultimate_accountable_id="committee_claims",
            ultimate_accountable_role="claims_committee",
        )
        
        request = DecisionRequest(
            decision_type=DecisionTypeEnum.BOUNDED,
            module_name="fnol_triage",
            input_data={"claim_amount": 500.0},
            user_id="user_123",
            ownership=ownership,
            accountability_scope=BOUNDED_LOW_SCOPE,
        )
        
        # Should not raise
        request.enforce_ownership_requirements()
