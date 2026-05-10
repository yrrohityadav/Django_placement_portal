# users/urls.py

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterAPIView,
    LoginAPIView,
    StudentProfileAPIView,
    CompanyProfileAPIView,
)

# WHY TokenRefreshView?
# ─────────────────────────────────────────────────────────────
# SimpleJWT provides this view built-in.
# When the access token expires (after 60 minutes), the client
# sends the refresh token to this endpoint and gets a new
# access token — without asking the user to log in again.
# ─────────────────────────────────────────────────────────────

urlpatterns = [
    # ── Authentication ─────────────────────────────────────────
    # POST /api/auth/register/  → Register as student or company
    path("auth/register/", RegisterAPIView.as_view(), name="auth-register"),

    # POST /api/auth/login/     → Login and receive JWT tokens
    path("auth/login/", LoginAPIView.as_view(), name="auth-login"),

    # POST /api/auth/token/refresh/  → Get new access token using refresh token
    # Body: { "refresh": "<your_refresh_token>" }
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # ── Student Profile ─────────────────────────────────────────
    # GET  /api/students/profile/  → View own profile
    # PUT  /api/students/profile/  → Update skills and/or resume
    path("students/profile/", StudentProfileAPIView.as_view(), name="student-profile"),

    # ── Company Profile ─────────────────────────────────────────
    # GET  /api/company/profile/   → View own profile
    # PUT  /api/company/profile/   → Update company name and description
    path("company/profile/", CompanyProfileAPIView.as_view(), name="company-profile"),
]
