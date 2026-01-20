"""Decision Boundary Enforcement.

Provides boundary checking to determine when human review is required.
Boundary violations automatically trigger human-in-the-loop.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class BoundaryType(str, Enum):
    """Types of boundaries that can be checked."""
    
    MONETARY = "monetary"  # Dollar amount thresholds
    CONFIDENCE = "confidence"  # Model confidence thresholds
    RISK = "risk"  # Risk score thresholds
    COMPLEXITY = "complexity"  # Decision complexity thresholds
    REGULATORY = "regulatory"  # Regulatory compliance requirements
    POLICY = "policy"  # Business policy constraints


class BoundaryCheck(BaseModel):
    """A single boundary check with pass/fail result.
    
    Attributes:
        boundary_type: The type of boundary being checked
        name: Human-readable name of the boundary
        threshold: The threshold value (if applicable)
        actual_value: The actual value being checked
        passed: Whether the boundary check passed
        reason: Human-readable explanation of the result
    """
    
    boundary_type: BoundaryType = Field(
        ..., description="Type of boundary being checked"
    )
    name: str = Field(..., description="Human-readable boundary name")
    threshold: Optional[float] = Field(
        None, description="Threshold value (if numeric)"
    )
    actual_value: Optional[float] = Field(
        None, description="Actual value being checked"
    )
    passed: bool = Field(..., description="Whether the check passed")
    reason: str = Field(
        ..., description="Human-readable explanation of the result"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "boundary_type": "monetary",
                "name": "High Value Claim Threshold",
                "threshold": 50000.0,
                "actual_value": 75000.0,
                "passed": False,
                "reason": "Claim amount $75,000 exceeds auto-approval threshold of $50,000"
            }
        }


class BoundaryResult(BaseModel):
    """Result of all boundary checks for a decision.
    
    Attributes:
        checks: List of individual boundary checks performed
        all_passed: Whether all boundary checks passed
        failed_checks: List of checks that failed
        human_review_reason: Consolidated reason for human review (if required)
    """
    
    checks: List[BoundaryCheck] = Field(
        default_factory=list, description="All boundary checks performed"
    )
    all_passed: bool = Field(
        ..., description="Whether all boundary checks passed"
    )
    failed_checks: List[BoundaryCheck] = Field(
        default_factory=list, description="Checks that failed"
    )
    human_review_reason: Optional[str] = Field(
        None, description="Consolidated reason for human review"
    )
    
    def requires_human(self) -> bool:
        """Determine if human review is required based on boundary checks.
        
        Returns:
            True if any boundary check failed, False otherwise.
        """
        return not self.all_passed
    
    def get_failed_boundary_types(self) -> List[BoundaryType]:
        """Get list of boundary types that failed.
        
        Returns:
            List of unique boundary types that failed.
        """
        return list(set(check.boundary_type for check in self.failed_checks))
    
    def get_failure_summary(self) -> str:
        """Get a human-readable summary of all failures.
        
        Returns:
            Formatted string summarizing all failed checks.
        """
        if self.all_passed:
            return "All boundary checks passed"
        
        summaries = [check.reason for check in self.failed_checks]
        return "; ".join(summaries)
    
    class Config:
        json_schema_extra = {
            "example": {
                "checks": [
                    {
                        "boundary_type": "monetary",
                        "name": "High Value Threshold",
                        "threshold": 50000.0,
                        "actual_value": 75000.0,
                        "passed": False,
                        "reason": "Exceeds $50K threshold"
                    },
                    {
                        "boundary_type": "confidence",
                        "name": "Minimum Confidence",
                        "threshold": 0.8,
                        "actual_value": 0.95,
                        "passed": True,
                        "reason": "Confidence above threshold"
                    }
                ],
                "all_passed": False,
                "failed_checks": [
                    {
                        "boundary_type": "monetary",
                        "name": "High Value Threshold",
                        "threshold": 50000.0,
                        "actual_value": 75000.0,
                        "passed": False,
                        "reason": "Exceeds $50K threshold"
                    }
                ],
                "human_review_reason": "High-value claim requires adjuster review"
            }
        }


def create_boundary_result(
    checks: List[BoundaryCheck],
    human_review_reason: Optional[str] = None
) -> BoundaryResult:
    """Helper function to create a BoundaryResult from checks.
    
    Args:
        checks: List of boundary checks performed
        human_review_reason: Optional custom reason for human review
    
    Returns:
        BoundaryResult with all_passed and failed_checks computed.
    """
    failed = [check for check in checks if not check.passed]
    all_passed = len(failed) == 0
    
    if human_review_reason is None and not all_passed:
        human_review_reason = f"{len(failed)} boundary check(s) failed"
    
    return BoundaryResult(
        checks=checks,
        all_passed=all_passed,
        failed_checks=failed,
        human_review_reason=human_review_reason
    )
