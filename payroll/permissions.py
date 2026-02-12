from rest_framework.permissions import BasePermission

from orgs.models import Membership, Organization


EMPLOYER_ROLES = {"owner", "admin", "employer"}
EMPLOYEE_ROLES = {"employee"}


class IsEmployerRole(BasePermission):
    def has_permission(self, request, view):
        org_id = getattr(view, "org_id", None) or request.data.get("org_id") or request.query_params.get("org_id")
        if not org_id:
            return False

        if Organization.objects.filter(id=org_id, owner=request.user).exists():
            return True

        membership = Membership.objects.filter(user=request.user, org_id=org_id).first()
        return bool(membership and membership.role in EMPLOYER_ROLES)


class IsEmployeeRole(BasePermission):
    def has_permission(self, request, view):
        org_id = getattr(view, "org_id", None) or request.query_params.get("org_id")
        if not org_id:
            return False

        membership = Membership.objects.filter(user=request.user, org_id=org_id).first()
        return bool(membership and membership.role in EMPLOYEE_ROLES)
