"""
FNOL Triage Engine

Extracted from: deevo-fnol-fast-triage/backend/ai/triage_engine.py
Purpose: Rule-based triage engine for FNOL scoring
"""

from typing import Dict, List, Any, Callable
from .models import FNOLInput, FNOLResult, TriageCategory, TriageRule, CustomerInfo, PolicyInfo


class FNOLTriageEngine:
    """
    Rule-based triage engine for FNOL scoring.
    
    Scoring Rules:
    - Young driver (< 25 years): +20 points
    - Motor product: +15 points
    - High estimated cost (> $1000): +15 points
    - Suspicious keywords in description: +10 points
    - High previous claims (> 2): +15 points
    
    Triage Categories:
    - Score <= 20: GREEN (low risk)
    - Score <= 40: YELLOW (medium risk)
    - Score > 40: RED (high risk)
    """
    
    SUSPICIOUS_KEYWORDS = [
        "lost", "unknown", "stolen", "missing", "disappeared",
        "can't find", "don't know", "not sure", "maybe",
        "suspicious", "fraud", "fake", "lie", "lying"
    ]
    
    def __init__(self):
        self.rules: List[Callable] = [
            self._check_young_driver,
            self._check_motor_product,
            self._check_high_cost,
            self._check_suspicious_description,
            self._check_previous_claims
        ]
    
    def triage(self, fnol_input: FNOLInput) -> FNOLResult:
        """
        Perform triage on FNOL claim.
        
        Args:
            fnol_input: FNOL input data
        
        Returns:
            FNOLResult with score, category, and recommendations
        """
        score = 0
        applied_rules = []
        rule_details = []
        
        # Apply each rule
        for rule in self.rules:
            rule_result = rule(fnol_input)
            
            rule_detail = TriageRule(
                rule_name=rule_result["rule_name"],
                description=rule_result["description"],
                points=rule_result["points"],
                triggered=rule_result["triggered"]
            )
            rule_details.append(rule_detail)
            
            if rule_result["triggered"]:
                score += rule_result["points"]
                applied_rules.append(rule_result["rule_name"])
        
        # Determine category
        if score <= 20:
            category = TriageCategory.GREEN
        elif score <= 40:
            category = TriageCategory.YELLOW
        else:
            category = TriageCategory.RED
        
        # Get risk description
        risk_level = self._get_risk_description(category)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(category, applied_rules)
        
        # Determine priority
        priority = self._determine_priority(category)
        
        # Estimate processing time
        estimated_time = self._estimate_processing_time(category)
        
        # Generate next steps
        next_steps = self._generate_next_steps(category, applied_rules)
        
        return FNOLResult(
            claim_id=fnol_input.claim_id,
            score=score,
            category=category,
            risk_level=risk_level,
            applied_rules=applied_rules,
            rule_details=rule_details,
            recommendation=recommendation,
            priority=priority,
            estimated_processing_time=estimated_time,
            next_steps=next_steps
        )
    
    def _check_young_driver(self, fnol_input: FNOLInput) -> Dict[str, Any]:
        """Check if customer is a young driver (< 25 years)."""
        triggered = fnol_input.customer.age < 25
        return {
            "triggered": triggered,
            "points": 20 if triggered else 0,
            "rule_name": "young_driver",
            "description": f"Customer is {fnol_input.customer.age} years old (under 25)"
        }
    
    def _check_motor_product(self, fnol_input: FNOLInput) -> Dict[str, Any]:
        """Check if policy is motor insurance."""
        triggered = fnol_input.policy.product_type.lower() == "motor"
        return {
            "triggered": triggered,
            "points": 15 if triggered else 0,
            "rule_name": "motor_product",
            "description": "Policy is motor insurance"
        }
    
    def _check_high_cost(self, fnol_input: FNOLInput) -> Dict[str, Any]:
        """Check if estimated cost is high (> $1000)."""
        triggered = fnol_input.estimated_cost > 1000
        return {
            "triggered": triggered,
            "points": 15 if triggered else 0,
            "rule_name": "high_cost",
            "description": f"Estimated cost ${fnol_input.estimated_cost:,.2f} exceeds $1,000 threshold"
        }
    
    def _check_suspicious_description(self, fnol_input: FNOLInput) -> Dict[str, Any]:
        """Check if description contains suspicious keywords."""
        description_lower = fnol_input.description.lower()
        found_keywords = [
            keyword for keyword in self.SUSPICIOUS_KEYWORDS 
            if keyword in description_lower
        ]
        triggered = len(found_keywords) > 0
        
        description = "Description contains suspicious keywords"
        if triggered:
            description += f": {', '.join(found_keywords[:3])}"
        
        return {
            "triggered": triggered,
            "points": 10 if triggered else 0,
            "rule_name": "suspicious_description",
            "description": description
        }
    
    def _check_previous_claims(self, fnol_input: FNOLInput) -> Dict[str, Any]:
        """Check if customer has high number of previous claims."""
        triggered = fnol_input.customer.previous_claims > 2
        return {
            "triggered": triggered,
            "points": 15 if triggered else 0,
            "rule_name": "high_previous_claims",
            "description": f"Customer has {fnol_input.customer.previous_claims} previous claims (threshold: 2)"
        }
    
    def _get_risk_description(self, category: TriageCategory) -> str:
        """Get human-readable risk description."""
        descriptions = {
            TriageCategory.GREEN: "Low risk - Standard processing",
            TriageCategory.YELLOW: "Medium risk - Additional review recommended",
            TriageCategory.RED: "High risk - Immediate investigation required"
        }
        return descriptions.get(category, "Unknown risk level")
    
    def _generate_recommendation(self, category: TriageCategory, applied_rules: List[str]) -> str:
        """Generate recommendation based on triage result."""
        if category == TriageCategory.GREEN:
            return (
                "This claim can proceed through standard processing. "
                "No additional investigation required at this time."
            )
        elif category == TriageCategory.YELLOW:
            return (
                "This claim requires additional review before processing. "
                "Assign to experienced adjuster for verification of details."
            )
        else:  # RED
            return (
                "This claim requires immediate investigation. "
                "Escalate to senior adjuster or fraud investigation team. "
                "Do not process until thorough review is completed."
            )
    
    def _determine_priority(self, category: TriageCategory) -> str:
        """Determine processing priority."""
        priority_map = {
            TriageCategory.GREEN: "low",
            TriageCategory.YELLOW: "medium",
            TriageCategory.RED: "high"
        }
        return priority_map.get(category, "medium")
    
    def _estimate_processing_time(self, category: TriageCategory) -> str:
        """Estimate processing time based on category."""
        time_map = {
            TriageCategory.GREEN: "1-2 business days",
            TriageCategory.YELLOW: "3-5 business days",
            TriageCategory.RED: "5-10 business days (pending investigation)"
        }
        return time_map.get(category, "Unknown")
    
    def _generate_next_steps(self, category: TriageCategory, applied_rules: List[str]) -> List[str]:
        """Generate next steps based on triage result."""
        steps = []
        
        if category == TriageCategory.GREEN:
            steps = [
                "Assign to standard claims queue",
                "Verify policy coverage",
                "Request supporting documentation",
                "Process claim according to standard procedures"
            ]
        elif category == TriageCategory.YELLOW:
            steps = [
                "Assign to experienced adjuster",
                "Verify all claim details",
                "Request additional documentation",
                "Conduct phone interview with claimant",
                "Review for consistency with policy terms"
            ]
        else:  # RED
            steps = [
                "Escalate to senior adjuster immediately",
                "Flag for fraud investigation team",
                "Request comprehensive documentation",
                "Conduct detailed investigation",
                "Verify incident details with third parties",
                "Do not approve payment until investigation complete"
            ]
        
        # Add specific steps based on triggered rules
        if "suspicious_description" in applied_rules:
            steps.append("Review claim description for inconsistencies")
        
        if "young_driver" in applied_rules and "motor_product" in applied_rules:
            steps.append("Verify driver's license and driving history")
        
        if "high_cost" in applied_rules:
            steps.append("Obtain independent cost estimate")
        
        return steps
    
    def get_rule_explanations(self) -> Dict[str, str]:
        """Get explanations for all rules."""
        return {
            "young_driver": "Customers under 25 years old (+20 points)",
            "motor_product": "Motor insurance policies (+15 points)",
            "high_cost": "Claims with estimated cost > $1,000 (+15 points)",
            "suspicious_description": "Descriptions with suspicious keywords (+10 points)",
            "high_previous_claims": "Customers with > 2 previous claims (+15 points)"
        }
