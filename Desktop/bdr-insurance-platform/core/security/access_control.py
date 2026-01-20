"""
Access Control

Provides fine-grained access control for resources.
"""

from typing import List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class AccessLevel(str, Enum):
    """Access levels for resources."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class AccessPolicy(BaseModel):
    """Access policy for a resource."""
    resource_type: str  # e.g., "decision", "module", "dataset"
    resource_id: str
    principal_type: str  # "user" or "role"
    principal_id: str
    access_level: AccessLevel
    conditions: dict = Field(default_factory=dict)


class AccessControlList:
    """
    Manages access control lists for resources.
    
    Provides fine-grained access control beyond role-based permissions.
    """
    
    def __init__(self):
        """Initialize access control list."""
        self._policies: List[AccessPolicy] = []
    
    def add_policy(self, policy: AccessPolicy) -> None:
        """Add an access policy."""
        self._policies.append(policy)
        logger.info(
            f"Added access policy: {policy.principal_id} -> "
            f"{policy.resource_type}:{policy.resource_id} ({policy.access_level})"
        )
    
    def check_access(
        self,
        user_id: str,
        user_roles: Set[str],
        resource_type: str,
        resource_id: str,
        required_level: AccessLevel
    ) -> bool:
        """
        Check if a user has access to a resource.
        
        Args:
            user_id: User identifier
            user_roles: User's roles
            resource_type: Type of resource
            resource_id: Resource identifier
            required_level: Required access level
            
        Returns:
            True if access is granted, False otherwise
        """
        # Check user-specific policies
        for policy in self._policies:
            if (
                policy.resource_type == resource_type
                and policy.resource_id == resource_id
                and policy.principal_type == "user"
                and policy.principal_id == user_id
            ):
                if self._access_level_sufficient(policy.access_level, required_level):
                    return True
        
        # Check role-based policies
        for policy in self._policies:
            if (
                policy.resource_type == resource_type
                and policy.resource_id == resource_id
                and policy.principal_type == "role"
                and policy.principal_id in user_roles
            ):
                if self._access_level_sufficient(policy.access_level, required_level):
                    return True
        
        return False
    
    def _access_level_sufficient(
        self,
        granted: AccessLevel,
        required: AccessLevel
    ) -> bool:
        """Check if granted access level is sufficient."""
        levels = {
            AccessLevel.NONE: 0,
            AccessLevel.READ: 1,
            AccessLevel.WRITE: 2,
            AccessLevel.ADMIN: 3,
        }
        
        return levels[granted] >= levels[required]
    
    def get_accessible_resources(
        self,
        user_id: str,
        user_roles: Set[str],
        resource_type: str,
        min_level: AccessLevel = AccessLevel.READ
    ) -> List[str]:
        """
        Get all resources of a type accessible to a user.
        
        Args:
            user_id: User identifier
            user_roles: User's roles
            resource_type: Type of resource
            min_level: Minimum access level required
            
        Returns:
            List of resource IDs
        """
        accessible = set()
        
        for policy in self._policies:
            if policy.resource_type != resource_type:
                continue
            
            # Check if policy applies to this user
            applies = False
            if policy.principal_type == "user" and policy.principal_id == user_id:
                applies = True
            elif policy.principal_type == "role" and policy.principal_id in user_roles:
                applies = True
            
            if applies and self._access_level_sufficient(policy.access_level, min_level):
                accessible.add(policy.resource_id)
        
        return list(accessible)
