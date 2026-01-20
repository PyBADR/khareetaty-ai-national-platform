"""
Security Module

Provides authentication, authorization, and access control
for all platform operations.
"""

from .auth import AuthenticationManager, AuthToken, UserIdentity
from .authz import AuthorizationManager, Permission, Role, require_permission
from .access_control import AccessControlList, AccessPolicy

__all__ = [
    'AuthenticationManager',
    'AuthToken',
    'UserIdentity',
    'AuthorizationManager',
    'Permission',
    'Role',
    'AccessControlList',
    'AccessPolicy',
    'require_permission',
]
