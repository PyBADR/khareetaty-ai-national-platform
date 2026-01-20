"""Decision Classification Enums.

Defines the three allowed decision types for the platform.
No additional decision types are permitted.
"""

from enum import Enum


class DecisionType(str, Enum):
    """Classification of decision types in the insurance platform.
    
    ADVISORY: Provides recommendations but requires human final decision.
              Example: Fraud risk indicators for investigator review.
    
    BOUNDED: Makes decisions within strict policy boundaries.
             Requires human review if boundaries are violated.
             Example: Auto-approve claims under $5K with no red flags.
    
    SIMULATION: What-if analysis with no real-world action.
                Example: Reinsurance treaty pricing scenarios.
    """
    
    ADVISORY = "advisory"
    BOUNDED = "bounded"
    SIMULATION = "simulation"
    
    def is_actionable(self) -> bool:
        """Check if this decision type can result in automated action.
        
        Returns:
            True only for BOUNDED decisions that pass all boundary checks.
        """
        return self == DecisionType.BOUNDED
    
    def requires_human_by_default(self) -> bool:
        """Check if this decision type requires human review by default.
        
        Returns:
            True for ADVISORY (always requires human).
            False for BOUNDED and SIMULATION (depends on boundary checks).
        """
        return self == DecisionType.ADVISORY
