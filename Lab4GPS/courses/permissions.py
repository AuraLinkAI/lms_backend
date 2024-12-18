from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):
    """
    Allows access only to instructors.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'instructor'

class IsStudent(BasePermission):
    """
    Allows access only to students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsAdmin(BasePermission):
    """
    Allows access only to admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
