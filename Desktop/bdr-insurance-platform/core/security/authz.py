"""
Authorization Manager

Handles role-based access control and permissions.
"""

from typing import List, Set, Optional
from enum import Enum
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions."""
    # Decision permissions
    DECISION_CREATE = "decision:create"
    DECISION_READ = "decision:read"
    DECISION_APPROVE = "decision:approve"
    DECISION_EXECUTE = "decision:execute"
    
    # Module permissions
    MODULE_FNOL = "module:fnol"
    MODULE_FRAUD = "module:fraud"
    MODULE_IFRS = "module:ifrs"
    MODULE_UNDERWRITING = "module:underwriting"
    MODULE_REINSURANCE = "module:reinsurance"
    
    # Admin permissions
    ADMIN_POLICY = "admin:policy"
    ADMIN_USER = "admin:user"
    ADMIN_AUDIT = "admin:audit"


class Role(BaseModel):
    """User role definition."""
    role_id: str
    name: str
    description: str
    permissions: Set[Permission] = Field(default_factory=set)
    inherits_from: List[str] = Field(default_factory=list)


class AuthorizationManager:
    """
    Manages role-based access control.
    
    Enforces permissions for all platform operations.
    """
    
    def __init__(self):
        """Initialize authorization manager with default roles."""
        self.roles: dict[str, Role] = {}
        self._user_roles: dict[str, Set[str]] = {}
        
        # Define default roles
        self._initialize_default_roles()
    
    def _initialize_default_roles(self) -> None:
        """Initialize default role hierarchy."""
        # Adjuster role
        self.add_role(Role(
            role_id="adjuster",
            name="Claims Adjuster",
            description="Can create and review FNOL decisions",
            permissions={
                Permission.DECISION_CREATE,
                Permission.DECISION_READ,
                Permission.MODULE_FNOL,
            }
        ))
        
        # Fraud Analyst role
        self.add_role(Role(
            role_id="fraud_analyst",
            name="Fraud Analyst",
            description="Can review fraud detection results",
            permissions={
                Permission.DECISION_READ,
                Permission.MODULE_FRAUD,
            }
        ))
        
        # Underwriter role
        self.add_role(Role(
            role_id="underwriter",
            name="Underwriter",
            description="Can create and approve underwriting decisions",
            permissions={
                Permission.DECISION_CREATE,
                Permission.DECISION_READ,
                Permission.DECISION_APPROVE,
                Permission.MODULE_UNDERWRITING,
            }
        ))
        
        # Manager role
        self.add_role(Role(
            role_id="manager",
            name="Manager",
            description="Can approve high-value decisions",
            permissions={
                Permission.DECISION_CREATE,
                Permission.DECISION_READ,
                Permission.DECISION_APPROVE,
                Permission.DECISION_EXECUTE,
                Permission.MODULE_FNOL,
                Permission.MODULE_FRAUD,
                Permission.MODULE_UNDERWRITING,
            }
        ))
        
        # Admin role
        self.add_role(Role(
            role_id="admin",
            name="Administrator",
            description="Full system access",
            permissions=set(Permission)  # All permissions
        ))
    
    def add_role(self, role: Role) -> None:
        """Add a role to the system."""
        self.roles[role.role_id] = role
        logger.info(f"Added role: {role.name}")
    
    def assign_role(self, user_id: str, role_id: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User identifier
            role_id: Role identifier
            
        Returns:
            True if role was assigned, False if role doesn't exist
        """
        if role_id not in self.roles:
            logger.warning(f"Role not found: {role_id}")
            return False
        
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
        
        self._user_roles[user_id].add(role_id)
        logger.info(f"Assigned role {role_id} to user {user_id}")
        return True
    
    def check_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user_id: User identifier
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        user_roles = self._user_roles.get(user_id, set())
        
        for role_id in user_roles:
            role = self.roles.get(role_id)
            if role and permission in role.permissions:
                return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Set of permissions
        """
        permissions = set()
        user_roles = self._user_roles.get(user_id, set())
        
        for role_id in user_roles:
            role = self.roles.get(role_id)
            if role:
                permissions.update(role.permissions)
        
        return permissions
    
    def require_permission(
        self,
        user_id: str,
        permission: Permission
    ) -> None:
        """
        Require a user to have a specific permission.
        
        Args:
            user_id: User identifier
            permission: Required permission
            
        Raises:
            PermissionError: If user doesn't have permission
        """
        if not self.check_permission(user_id, permission):
            raise PermissionError(
                f"User {user_id} does not have permission: {permission}"
            )


# Decorator for permission checking
def require_permission(permission_str: str):
    """Decorator to require a permission for a function.
    
    Args:
        permission_str: Permission string (e.g., 'fnol:triage')
    
    Returns:
        Decorator function
    
    Note:
        This is a simplified decorator for contract compliance.
        In production, this should integrate with the AuthorizationManager.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # TODO(security): Integrate with AuthorizationManager
            # For now, this is a pass-through for contract compliance
            logger.debug(f"Permission check: {permission_str} (not enforced in dev mode)")
            return func(*args, **kwargs)
        return wrapper
    return decorator
