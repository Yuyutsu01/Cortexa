"""Domain Enums Module.

Defines strongly-typed enumerations for RBAC roles, audit actions, and entity statuses.
"""

from enum import StrEnum


class UserRole(StrEnum):
    """Role-Based Access Control (RBAC) levels within an Organization."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

    @classmethod
    def can_manage_roles(cls, role: "UserRole") -> bool:
        """Check if role has permission to change member roles."""
        return role in (cls.OWNER, cls.ADMIN)

    @classmethod
    def can_manage_organization(cls, role: "UserRole") -> bool:
        """Check if role has permission to update organization settings."""
        return role in (cls.OWNER, cls.ADMIN)

    @classmethod
    def can_delete_organization(cls, role: "UserRole") -> bool:
        """Check if role has permission to delete the organization."""
        return role == cls.OWNER


class OrgStatus(StrEnum):
    """Lifecycle status of an Organization."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class AuditAction(StrEnum):
    """Audited domain actions recorded in the system."""

    # User lifecycle actions
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_UPDATED = "user.updated"
    USER_DEACTIVATED = "user.deactivated"

    # Organization actions
    ORG_CREATED = "organization.created"
    ORG_UPDATED = "organization.updated"
    ORG_ARCHIVED = "organization.archived"

    # Membership & RBAC actions
    MEMBER_ADDED = "membership.added"
    MEMBER_ROLE_CHANGED = "membership.role_changed"
    MEMBER_REMOVED = "membership.removed"
