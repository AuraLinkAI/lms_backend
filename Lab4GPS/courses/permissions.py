# courses/permissions.py
from rest_framework.permissions import BasePermission
from Auths.models import CustomUser  # Ensure this import is correct based on your project structure

class IsInstructor(BasePermission):
    """
    Allows access only to instructors.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == CustomUser.Roles.INSTRUCTOR.value

class IsStudent(BasePermission):
    """
    Allows access only to students.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == CustomUser.Roles.STUDENT.value

class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
