# auth/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOtpView,
    LoginView,
    UserProfileView,
    UpdateProfileView,
    UpdateProfilePictureView,
    ChangePasswordView,
    ForgotPasswordView,
    VerifyResetOtpView,
    ResetPasswordView,
    UserListView,
    UserDetailView,  # <-- NEW
)

urlpatterns = [
    # Existing endpoints
    path('signup/', RegisterView.as_view(), name='signup'),
    path('verify-otp/', VerifyOtpView.as_view(), name='verify_otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/update-picture/', UpdateProfilePictureView.as_view(), name='update_profile_picture'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-reset-otp/', VerifyResetOtpView.as_view(), name='verify_reset_otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),

    # Admin-only endpoints
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),  # <--- NEW
]
