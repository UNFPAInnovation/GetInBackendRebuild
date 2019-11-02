from rest_framework import permissions


class IsPostOrIsAuthenticated(permissions.BasePermission):
    # Allows the user to only send data to server,
    # however user will be prohibited from retrieving information from any view with this permission

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
        return request.user and request.user.is_authenticated
