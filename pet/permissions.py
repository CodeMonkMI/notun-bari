from rest_framework import permissions


class IsAuthenticatedOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if not request.user.is_staff and view.action in ["create"]:
            return True
        return False
