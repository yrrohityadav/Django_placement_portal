# users/views.py
#
# HOW JWT AUTHENTICATION FLOW WORKS (end to end):
# ─────────────────────────────────────────────────────────────
# STEP 1: User registers → account created in database
#
# STEP 2: User logs in with username + password
#         → Server verifies credentials
#         → Server creates and returns: ACCESS TOKEN + REFRESH TOKEN
#
# STEP 3: User stores both tokens (Postman saves them automatically)
#
# STEP 4: User makes a request to a protected API
#         → Adds header: Authorization: Bearer <access_token>
#         → JWTAuthentication middleware reads the header
#         → Decodes and verifies the token (no database lookup needed!)
#         → Sets request.user = the user from the token
#
# STEP 5: When access token expires (after 60 minutes):
#         → User sends refresh token to /api/auth/token/refresh/
#         → Gets a new access token WITHOUT logging in again
#
# STEP 6: When refresh token expires (after 7 days):
#         → User must log in again
# ─────────────────────────────────────────────────────────────

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import StudentProfile, CompanyProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    StudentProfileSerializer,
    CompanyProfileSerializer,
)
from .permissions import IsStudent, IsCompany

User = get_user_model()


# ══════════════════════════════════════════════════════════════
# REGISTER API VIEW
# Endpoint: POST /api/auth/register/
# Auth required: NO (anyone can register)
# ══════════════════════════════════════════════════════════════
class RegisterAPIView(APIView):
    """
    Register a new user (student or company).
    Auto-creates related profile via Django signal (already in models.py).

    permission_classes = [AllowAny] overrides the global default
    (IsAuthenticated) so that unauthenticated users CAN access this.
    This makes sense — how can you log in if you can't register?
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Pass request.data (JSON from Postman) into the serializer
        serializer = RegisterSerializer(data=request.data)

        # is_valid() runs all validations (field validators + validate_*())
        # raise_exception=True means if invalid, DRF auto-returns 400
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {
                    "message": "Registration successful!",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )


# ══════════════════════════════════════════════════════════════
# LOGIN API VIEW
# Endpoint: POST /api/auth/login/
# Auth required: NO (you can't authenticate before logging in)
# ══════════════════════════════════════════════════════════════
class LoginAPIView(APIView):
    """
    Login with username + password.
    Returns: access token, refresh token, and user info.

    The ACCESS TOKEN is what you put in the Authorization header
    for all future requests:
        Authorization: Bearer <your_access_token>
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # The LoginSerializer.validate() already built the response dict
            return Response(serializer.validated_data, status=status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════
# STUDENT PROFILE VIEW
# Endpoint: GET /api/students/profile/
#           PUT /api/students/profile/
# Auth required: YES, and must be a student
# ══════════════════════════════════════════════════════════════
class StudentProfileAPIView(APIView):
    """
    Students view and update their own profile.

    [IsAuthenticated, IsStudent] = BOTH conditions must be true:
    1. User must have a valid JWT token
    2. User's role must be 'student'

    request.user is automatically set by JWTAuthentication
    based on the token — the student cannot spoof another user.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            # request.user is the logged-in student from the JWT token
            profile = StudentProfile.objects.get(user=request.user)
            serializer = StudentProfileSerializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            # 404 if profile somehow doesn't exist
            return Response(
                {"error": "Student profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request):
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            return Response(
                {"error": "Student profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # partial=True means fields are optional — student can update
        # just skills OR just resume, they don't need to send both
        serializer = StudentProfileSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "Profile updated successfully.", "data": serializer.data}
            )


# ══════════════════════════════════════════════════════════════
# COMPANY PROFILE VIEW
# Endpoint: GET /api/company/profile/
#           PUT /api/company/profile/
# Auth required: YES, and must be a company
# ══════════════════════════════════════════════════════════════
class CompanyProfileAPIView(APIView):
    """
    Companies view and update their own profile.
    """
    permission_classes = [IsAuthenticated, IsCompany]

    def get(self, request):
        try:
            profile = CompanyProfile.objects.get(user=request.user)
            serializer = CompanyProfileSerializer(profile)
            return Response(serializer.data)
        except CompanyProfile.DoesNotExist:
            return Response(
                {"error": "Company profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request):
        try:
            profile = CompanyProfile.objects.get(user=request.user)
        except CompanyProfile.DoesNotExist:
            return Response(
                {"error": "Company profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CompanyProfileSerializer(
            profile, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "Profile updated successfully.", "data": serializer.data}
            )
