"""
Input and Justification Validators

Extracted from: insurance-hf-project/create_gradio_space.py
Purpose: Validate inputs and enforce human justification requirements
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a validation check"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    
    def __bool__(self):
        return self.is_valid


class InputValidator:
    """
    Validates input data for decision-making processes.
    
    Ensures data quality and completeness before processing.
    """
    
    def __init__(self):
        self.required_fields = set()
        self.numeric_ranges = {}
        self.custom_validators = {}
    
    def validate_claim_input(self, 
                            claim_id: str,
                            claim_amount: float,
                            **kwargs) -> ValidationResult:
        """
        Validate claim input data.
        
        Args:
            claim_id: Unique claim identifier
            claim_amount: Claim amount in currency
            **kwargs: Additional claim fields
        
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # Validate claim ID
        if not claim_id or not claim_id.strip():
            errors.append("Claim ID is required")
        
        # Validate claim amount
        if claim_amount <= 0:
            errors.append("Claim amount must be positive")
        elif claim_amount > 1_000_000:
            warnings.append(f"High claim amount: ${claim_amount:,.2f} - requires additional review")
        
        # Check for missing documentation
        if not kwargs.get('documentation_complete', False):
            warnings.append("Documentation is incomplete - may affect decision confidence")
        
        # Check for high-value claims without police report
        if claim_amount > 5000 and not kwargs.get('has_police_report', False):
            warnings.append("Police report recommended for claims over $5,000")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_required_fields(self, data: Dict[str, Any], 
                                required: List[str]) -> ValidationResult:
        """
        Validate that required fields are present and non-empty.
        
        Args:
            data: Input data dictionary
            required: List of required field names
        
        Returns:
            ValidationResult
        """
        errors = []
        
        for field in required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                errors.append(f"Field '{field}' cannot be empty")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=[]
        )


class JustificationValidator:
    """
    Validates human justification for decisions.
    
    Enforces that humans provide adequate reasoning for their decisions,
    ensuring accountability and auditability.
    """
    
    def __init__(self, min_length: int = 10, max_length: int = 5000):
        """
        Initialize validator.
        
        Args:
            min_length: Minimum justification length in characters
            max_length: Maximum justification length in characters
        """
        self.min_length = min_length
        self.max_length = max_length
    
    def validate(self, justification: str) -> ValidationResult:
        """
        Validate human justification text.
        
        Args:
            justification: Human-provided justification text
        
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check if justification exists
        if not justification or not justification.strip():
            errors.append("Human justification is required")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)
        
        justification = justification.strip()
        
        # Check minimum length
        if len(justification) < self.min_length:
            errors.append(
                f"Justification too short (minimum {self.min_length} characters). "
                f"Please provide detailed reasoning."
            )
        
        # Check maximum length
        if len(justification) > self.max_length:
            errors.append(
                f"Justification too long (maximum {self.max_length} characters). "
                f"Please be more concise."
            )
        
        # Check for generic/template responses
        generic_phrases = [
            "looks good",
            "seems fine",
            "ok",
            "approved",
            "rejected",
            "test",
            "asdf"
        ]
        
        justification_lower = justification.lower()
        if any(phrase in justification_lower for phrase in generic_phrases) and len(justification) < 50:
            warnings.append(
                "Justification appears generic. Please provide specific reasoning "
                "based on the case details."
            )
        
        # Check for sufficient detail (word count)
        word_count = len(justification.split())
        if word_count < 5:
            warnings.append(
                f"Justification is very brief ({word_count} words). "
                f"Consider providing more detail."
            )
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_with_context(self, 
                             justification: str,
                             decision_context: Dict[str, Any]) -> ValidationResult:
        """
        Validate justification with additional context.
        
        Args:
            justification: Human-provided justification
            decision_context: Context about the decision (risk level, amount, etc.)
        
        Returns:
            ValidationResult
        """
        # First do basic validation
        result = self.validate(justification)
        
        # Add context-specific checks
        if result.is_valid:
            risk_level = decision_context.get('risk_level', 'UNKNOWN')
            uncertainty_flag = decision_context.get('uncertainty_flag', False)
            
            # High-risk decisions need more detailed justification
            if risk_level == 'HIGH' and len(justification) < 100:
                result.warnings.append(
                    "High-risk decision detected. Consider providing more detailed justification."
                )
            
            # Uncertain decisions need explicit acknowledgment
            if uncertainty_flag and 'uncertain' not in justification.lower():
                result.warnings.append(
                    "System flagged high uncertainty. Consider acknowledging this in your justification."
                )
        
        return result


def validate_authority_in_response(response: Dict[str, Any]) -> ValidationResult:
    """Validate that DecisionResponse includes required authority metadata.
    
    CI enforcement: This validator MUST pass for all DecisionResponse objects.
    
    Args:
        response: The decision response dictionary
    
    Returns:
        ValidationResult with errors if authority metadata is missing
    """
    errors = []
    warnings = []
    
    # Required authority fields
    required_fields = [
        "authority_id",
        "authority_role",
        "authority_checks_passed",
        "authority_enforcement_timestamp"
    ]
    
    # Check for missing fields
    for field in required_fields:
        if field not in response:
            errors.append(f"Missing required authority field: {field}")
    
    # Validate authority_checks_passed is boolean
    if "authority_checks_passed" in response:
        if not isinstance(response["authority_checks_passed"], bool):
            errors.append("authority_checks_passed must be boolean")
    
    # Validate timestamp format
    if "authority_enforcement_timestamp" in response:
        timestamp = response["authority_enforcement_timestamp"]
        if not isinstance(timestamp, str):
            errors.append("authority_enforcement_timestamp must be ISO format string")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_authority_severity_match(
    authority: "DecisionAuthority",
    severity: "DecisionSeverity"
) -> ValidationResult:
    """Validate that authority can handle the given severity.
    
    CI enforcement: Prevents authority from executing beyond severity limits.
    
    Args:
        authority: The decision authority
        severity: The decision severity
    
    Returns:
        ValidationResult with errors if severity exceeds authority
    """
    errors = []
    warnings = []
    
    if severity.value > authority.max_decision_severity.value:
        errors.append(
            f"Authority '{authority.authority_id}' (max severity: {authority.max_decision_severity.name}) "
            f"cannot handle severity {severity.name}. Escalation required."
        )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_no_authority_bypass(
    decision_request: Dict[str, Any]
) -> ValidationResult:
    """Validate that override paths do not bypass authority checks.
    
    CI enforcement: Ensures all override paths require proper authority.
    
    Args:
        decision_request: The decision request dictionary
    
    Returns:
        ValidationResult with errors if authority bypass detected
    """
    errors = []
    warnings = []
    
    # Check if override is requested
    if decision_request.get("override_boundaries", False):
        # Must have authority metadata
        if "authority" not in decision_request:
            errors.append(
                "Boundary override requested without authority. "
                "All overrides must have explicit authority."
            )
        else:
            authority = decision_request["authority"]
            if not authority.get("can_override", False):
                errors.append(
                    f"Authority '{authority.get('authority_id')}' does not have override permission. "
                    "Override requires elevated authority."
                )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def validate_human_required_authority(
    authority: "DecisionAuthority",
    decision_request: Dict[str, Any]
) -> ValidationResult:
    """Validate that human-required authority has human signature.
    
    CI enforcement: Prevents automatic execution of human-required decisions.
    
    Args:
        authority: The decision authority
        decision_request: The decision request dictionary
    
    Returns:
        ValidationResult with errors if human signature missing
    """
    errors = []
    warnings = []
    
    if authority.requires_human_signature:
        metadata = decision_request.get("metadata", {})
        if not metadata.get("human_signature"):
            errors.append(
                f"Authority '{authority.authority_id}' requires human signature but none provided. "
                "Decision cannot execute automatically."
            )
    
    if authority.requires_committee:
        metadata = decision_request.get("metadata", {})
        if not metadata.get("committee_approval"):
            errors.append(
                f"Authority '{authority.authority_id}' requires committee approval but none provided. "
                "Decision cannot execute without committee review."
            )
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
