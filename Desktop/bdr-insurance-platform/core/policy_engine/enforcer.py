"""
Policy Enforcer

Validates decisions against business rules, constraints, and regulatory requirements.
"""

from typing import Any, Dict, List, Optional
import logging

from .models import Policy, Constraint, ValidationResult, PolicyType

logger = logging.getLogger(__name__)


class PolicyEnforcer:
    """
    Enforces business policies and regulatory constraints.
    
    This service validates decisions against configured policies
    before they are executed.
    """
    
    def __init__(self, policies: Optional[List[Policy]] = None):
        """
        Initialize the policy enforcer.
        
        Args:
            policies: List of policies to enforce
        """
        self.policies = policies or []
        self._active_policies = [p for p in self.policies if p.active]
        
    def add_policy(self, policy: Policy) -> None:
        """Add a new policy to the enforcer."""
        self.policies.append(policy)
        if policy.active:
            self._active_policies.append(policy)
            
    def validate_decision(self, decision: Any) -> ValidationResult:
        """
        Validate a decision against all active policies.
        
        Args:
            decision: Decision object to validate
            
        Returns:
            ValidationResult with violations and warnings
        """
        violations = []
        warnings = []
        policies_checked = []
        
        # Sort policies by priority (higher priority first)
        sorted_policies = sorted(
            self._active_policies,
            key=lambda p: p.priority,
            reverse=True
        )
        
        for policy in sorted_policies:
            policies_checked.append(policy.policy_id)
            
            try:
                # Check policy rules
                policy_result = self._check_policy(decision, policy)
                
                if not policy_result['is_valid']:
                    if policy.policy_type == PolicyType.REGULATORY:
                        # Regulatory violations are hard failures
                        violations.extend(policy_result['violations'])
                    else:
                        # Business/operational violations are warnings
                        warnings.extend(policy_result['violations'])
                        
            except Exception as e:
                logger.error(
                    f"Error checking policy {policy.policy_id}: {str(e)}",
                    exc_info=True
                )
                warnings.append(f"Policy check failed: {policy.name}")
        
        is_valid = len(violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            policies_checked=policies_checked
        )
    
    def _check_policy(self, decision: Any, policy: Policy) -> Dict[str, Any]:
        """
        Check a single policy against a decision.
        
        Args:
            decision: Decision to validate
            policy: Policy to check
            
        Returns:
            Dict with is_valid and violations
        """
        violations = []
        
        # TODO(platform): Implement actual policy rule evaluation
        # This is a placeholder that should be replaced with a proper
        # rule engine (e.g., using Python expressions, Rego, or similar)
        
        # Example rule checks:
        rules = policy.rules
        
        # Check confidence threshold
        if 'min_confidence' in rules:
            if hasattr(decision, 'result') and decision.result:
                if decision.result.confidence < rules['min_confidence']:
                    violations.append(
                        f"Confidence {decision.result.confidence} below "
                        f"minimum {rules['min_confidence']}"
                    )
        
        # Check required fields
        if 'required_fields' in rules:
            for field in rules['required_fields']:
                if not hasattr(decision, field) or getattr(decision, field) is None:
                    violations.append(f"Required field missing: {field}")
        
        # Check value constraints
        if 'constraints' in rules:
            for constraint_def in rules['constraints']:
                # Evaluate constraint
                # This is simplified - real implementation would use
                # a proper expression evaluator
                pass
        
        return {
            'is_valid': len(violations) == 0,
            'violations': violations
        }
    
    def validate_input(self, input_data: Dict[str, Any], constraints: List[Constraint]) -> ValidationResult:
        """
        Validate input data against constraints.
        
        Args:
            input_data: Input data to validate
            constraints: List of constraints to check
            
        Returns:
            ValidationResult
        """
        violations = []
        
        for constraint in constraints:
            # TODO(platform): Implement constraint evaluation
            # This should support various constraint types:
            # - Range checks (min/max)
            # - Type validation
            # - Format validation (regex)
            # - Business logic constraints
            pass
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=[],
            policies_checked=[]
        )
    
    def get_applicable_policies(
        self,
        decision_type: str,
        module_name: str
    ) -> List[Policy]:
        """
        Get policies applicable to a specific decision type and module.
        
        Args:
            decision_type: Type of decision
            module_name: Name of the calling module
            
        Returns:
            List of applicable policies
        """
        # Filter policies based on decision type and module
        applicable = []
        
        for policy in self._active_policies:
            # Check if policy applies to this decision type
            if 'decision_types' in policy.rules:
                if decision_type not in policy.rules['decision_types']:
                    continue
            
            # Check if policy applies to this module
            if 'modules' in policy.rules:
                if module_name not in policy.rules['modules']:
                    continue
            
            applicable.append(policy)
        
        return applicable
