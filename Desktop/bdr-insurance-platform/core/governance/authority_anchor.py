"""Authority Anchor Layer - Phase 2.2

This module implements legally attributable authority anchoring.
Every decision authority must be anchored to:
- A legal entity (company/organization)
- A jurisdiction (country/regulatory zone)
- A job title (contractual role)
- A contract reference (policy/HR/mandate)
- A time validity window

This ensures every production decision is legally attributable to a specific
human authority under a specific jurisdiction and mandate.

NO DECISION CAN EXECUTE IN PRODUCTION WITHOUT A VALID AUTHORITY ANCHOR.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from uuid import uuid4


class Jurisdiction(Enum):
    """Supported jurisdictions (ISO 3166-1 alpha-2 country codes)."""
    # Middle East
    KW = "KW"  # Kuwait
    SA = "SA"  # Saudi Arabia
    AE = "AE"  # United Arab Emirates
    BH = "BH"  # Bahrain
    QA = "QA"  # Qatar
    OM = "OM"  # Oman
    
    # Europe
    GB = "GB"  # United Kingdom
    DE = "DE"  # Germany
    FR = "FR"  # France
    
    # North America
    US = "US"  # United States
    CA = "CA"  # Canada
    
    # Asia Pacific
    SG = "SG"  # Singapore
    HK = "HK"  # Hong Kong
    AU = "AU"  # Australia


@dataclass(frozen=True)
class AuthorityAnchor:
    """Immutable legal anchor for decision authority.
    
    An AuthorityAnchor binds a decision authority to:
    - A legal entity (company/organization)
    - A jurisdiction (country/regulatory zone)
    - A job title (contractual role with legal standing)
    - A contract reference (employment contract, policy, mandate)
    - A time validity window (when this authority is valid)
    
    This ensures every decision is legally attributable and auditable.
    
    Attributes:
        anchor_id: Unique identifier for this anchor
        legal_entity: Full legal name of the company/organization
        jurisdiction: ISO country code or regulatory zone
        job_title: Contractual job title (e.g., "Senior Claims Manager")
        contract_reference: Reference to employment contract, policy, or mandate
        valid_from: When this authority becomes valid (UTC)
        valid_until: When this authority expires (None = indefinite)
        metadata: Additional anchor metadata
    """
    anchor_id: str
    legal_entity: str
    jurisdiction: Jurisdiction
    job_title: str
    contract_reference: str
    valid_from: datetime
    valid_until: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate authority anchor."""
        # Validate required fields are not empty
        if not self.anchor_id:
            raise ValueError("anchor_id cannot be empty")
        if not self.legal_entity or not self.legal_entity.strip():
            raise ValueError("legal_entity cannot be empty")
        if not self.job_title or not self.job_title.strip():
            raise ValueError("job_title cannot be empty")
        if not self.contract_reference or not self.contract_reference.strip():
            raise ValueError("contract_reference cannot be empty")
        
        # Validate time window
        if self.valid_until is not None:
            if self.valid_until <= self.valid_from:
                raise ValueError("valid_until must be after valid_from")
        
        # Ensure datetimes are timezone-aware (UTC)
        if self.valid_from.tzinfo is None:
            raise ValueError("valid_from must be timezone-aware (UTC)")
        if self.valid_until is not None and self.valid_until.tzinfo is None:
            raise ValueError("valid_until must be timezone-aware (UTC)")

    def is_valid_at(self, timestamp: datetime) -> bool:
        """Check if anchor is valid at a given timestamp.
        
        Args:
            timestamp: Timestamp to check (must be timezone-aware)
        
        Returns:
            True if anchor is valid at the given timestamp
        """
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware (UTC)")
        
        # Check if timestamp is within validity window
        if timestamp < self.valid_from:
            return False
        
        if self.valid_until is not None and timestamp >= self.valid_until:
            return False
        
        return True
    
    def is_currently_valid(self) -> bool:
        """Check if anchor is currently valid.
        
        Returns:
            True if anchor is valid at current UTC time
        """
        return self.is_valid_at(datetime.now(timezone.utc))
    
    def days_until_expiry(self) -> Optional[int]:
        """Get number of days until anchor expires.
        
        Returns:
            Number of days until expiry, or None if no expiry
        """
        if self.valid_until is None:
            return None
        
        now = datetime.now(timezone.utc)
        if now >= self.valid_until:
            return 0
        
        delta = self.valid_until - now
        return delta.days
    
    def matches_jurisdiction(self, required_jurisdiction: Jurisdiction) -> bool:
        """Check if anchor matches required jurisdiction.
        
        Args:
            required_jurisdiction: Required jurisdiction
        
        Returns:
            True if jurisdictions match
        """
        return self.jurisdiction == required_jurisdiction


@dataclass(frozen=True)
class AuthorityExplanation:
    """Structured explanation of authority decision.
    
    This explanation is attached to every DecisionResponse and provides
    human-readable and regulator-readable justification for why a decision
    was allowed or blocked based on authority.
    
    Attributes:
        why_allowed: Explanation of why decision was allowed (if allowed)
        why_blocked: Explanation of why decision was blocked (if blocked)
        governing_policy: Reference to governing policy/regulation
        anchor_details: Details of the authority anchor used
        timestamp: When this explanation was generated
    """
    why_allowed: Optional[str]
    why_blocked: Optional[str]
    governing_policy: str
    anchor_details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """Validate authority explanation."""
        # Must have either why_allowed or why_blocked (not both, not neither)
        has_allowed = self.why_allowed is not None and self.why_allowed.strip()
        has_blocked = self.why_blocked is not None and self.why_blocked.strip()
        
        if has_allowed and has_blocked:
            raise ValueError("Cannot have both why_allowed and why_blocked")
        if not has_allowed and not has_blocked:
            raise ValueError("Must have either why_allowed or why_blocked")
        
        if not self.governing_policy or not self.governing_policy.strip():
            raise ValueError("governing_policy cannot be empty")


def create_authority_anchor(
    legal_entity: str,
    jurisdiction: Jurisdiction,
    job_title: str,
    contract_reference: str,
    valid_from: datetime,
    valid_until: Optional[datetime] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AuthorityAnchor:
    """Create an authority anchor.
    
    Args:
        legal_entity: Full legal name of company/organization
        jurisdiction: ISO country code or regulatory zone
        job_title: Contractual job title
        contract_reference: Reference to contract/policy/mandate
        valid_from: When authority becomes valid (UTC)
        valid_until: When authority expires (None = indefinite)
        metadata: Additional metadata
    
    Returns:
        AuthorityAnchor instance
    """
    anchor_id = f"anchor_{jurisdiction.value}_{uuid4().hex[:12]}"
    
    return AuthorityAnchor(
        anchor_id=anchor_id,
        legal_entity=legal_entity,
        jurisdiction=jurisdiction,
        job_title=job_title,
        contract_reference=contract_reference,
        valid_from=valid_from,
        valid_until=valid_until,
        metadata=metadata or {}
    )


def validate_anchor_for_production(
    anchor: Optional[AuthorityAnchor],
    required_jurisdiction: Optional[Jurisdiction] = None
) -> tuple[bool, Optional[str]]:
    """Validate that an anchor is suitable for production use.
    
    Args:
        anchor: Authority anchor to validate (or None)
        required_jurisdiction: Required jurisdiction (or None for any)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # RULE 1: Anchor must exist
    if anchor is None:
        return False, "No authority anchor provided - production decisions require legal attribution"
    
    # RULE 2: Anchor must be currently valid
    if not anchor.is_currently_valid():
        now = datetime.now(timezone.utc)
        if now < anchor.valid_from:
            return False, f"Authority not yet valid (valid from {anchor.valid_from.isoformat()})"
        else:
            return False, f"Authority expired (expired at {anchor.valid_until.isoformat()})"
    
    # RULE 3: Jurisdiction must match (if specified)
    if required_jurisdiction is not None:
        if not anchor.matches_jurisdiction(required_jurisdiction):
            return False, f"Jurisdiction mismatch: anchor is {anchor.jurisdiction.value}, required {required_jurisdiction.value}"
    
    # RULE 4: Contract reference must be present
    if not anchor.contract_reference or not anchor.contract_reference.strip():
        return False, "Missing contract reference - cannot establish legal basis for authority"
    
    # RULE 5: Warn if expiring soon (within 30 days)
    days_left = anchor.days_until_expiry()
    if days_left is not None and days_left <= 30:
        # This is a warning, not a blocking error
        # In production, this should trigger a notification
        pass
    
    return True, None


def create_authority_explanation(
    allowed: bool,
    reason: str,
    governing_policy: str,
    anchor: Optional[AuthorityAnchor] = None
) -> AuthorityExplanation:
    """Create an authority explanation.
    
    Args:
        allowed: Whether decision was allowed
        reason: Reason for allowing or blocking
        governing_policy: Reference to governing policy
        anchor: Authority anchor (if available)
    
    Returns:
        AuthorityExplanation instance
    """
    anchor_details = {}
    if anchor is not None:
        anchor_details = {
            "anchor_id": anchor.anchor_id,
            "legal_entity": anchor.legal_entity,
            "jurisdiction": anchor.jurisdiction.value,
            "job_title": anchor.job_title,
            "contract_reference": anchor.contract_reference,
            "valid_from": anchor.valid_from.isoformat(),
            "valid_until": anchor.valid_until.isoformat() if anchor.valid_until else None,
        }
    
    return AuthorityExplanation(
        why_allowed=reason if allowed else None,
        why_blocked=reason if not allowed else None,
        governing_policy=governing_policy,
        anchor_details=anchor_details
    )


# Predefined Authority Anchors (Examples)

KUWAIT_CLAIMS_MANAGER_ANCHOR = create_authority_anchor(
    legal_entity="GIG Takaful Kuwait",
    jurisdiction=Jurisdiction.KW,
    job_title="Senior Claims Manager",
    contract_reference="EMP-2024-KW-CM-001",
    valid_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    valid_until=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
    metadata={
        "department": "Claims",
        "authority_level": "senior",
        "max_claim_amount": 50000,
    }
)

KUWAIT_DIRECTOR_ANCHOR = create_authority_anchor(
    legal_entity="GIG Takaful Kuwait",
    jurisdiction=Jurisdiction.KW,
    job_title="Director of Claims",
    contract_reference="EMP-2024-KW-DIR-001",
    valid_from=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
    valid_until=None,  # Indefinite
    metadata={
        "department": "Claims",
        "authority_level": "director",
        "max_claim_amount": 500000,
    }
)