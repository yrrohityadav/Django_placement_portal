# users/serializers.py
#
# WHY SERIALIZERS?
# ─────────────────────────────────────────────────────────────
# A serializer does TWO jobs:
#
# 1. VALIDATION — When data comes IN (from Postman), the serializer
#    checks: Is the email valid? Is the password long enough?
#    Did the user pick a valid role? etc.
#
# 2. CONVERSION — When data goes OUT (to Postman), the serializer
#    converts Python/Django objects into JSON that Postman can read.
#
# Think of it like a FORM that validates input AND formats output.
# ─────────────────────────────────────────────────────────────

from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import StudentProfile, CompanyProfile

# get_user_model() is Django best practice.
# Instead of directly importing our User class, we ask Django:
# "What is the current User model?" This is safer because if
# we ever swap our User model, this code still works.
User = get_user_model()


# ══════════════════════════════════════════════════════════════
# REGISTER SERIALIZER
# Used by: POST /api/auth/register/
# ══════════════════════════════════════════════════════════════
class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration.

    Fields:
    - username, email, password → standard user fields
    - role → must be 'student' or 'company' (not 'admin')
    - password is write_only so it NEVER appears in responses
    """

    # write_only=True means this field is accepted as INPUT but
    # never returned in the response (for security)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role"]
        # read_only_fields appear only in responses, not in input
        read_only_fields = ["id"]

    def validate_email(self, value):
        """
        Custom field-level validation for email.

        DRF calls validate_<fieldname>() automatically.
        We check if the email is already registered.
        If yes → raise ValidationError (returns 400 Bad Request).
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value

    def validate_role(self, value):
        """
        Custom validation: users cannot self-register as 'admin'.
        Admin accounts must be created via Django admin panel.
        """
        if value == "admin":
            raise serializers.ValidationError(
                "Cannot self-register as admin."
            )
        return value

    def create(self, validated_data):
        """
        create() is called by serializer.save().

        We use create_user() instead of create() because:
        create_user() automatically HASHES the password.
        If we used create(), the raw password would be stored — INSECURE!
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],  # gets hashed automatically
            role=validated_data["role"],
        )
        return user


# ══════════════════════════════════════════════════════════════
# LOGIN SERIALIZER
# Used by: POST /api/auth/login/
# ══════════════════════════════════════════════════════════════
class LoginSerializer(serializers.Serializer):
    """
    Handles user login.

    We use plain Serializer (not ModelSerializer) because we're
    not creating/reading a model — we're just validating credentials
    and generating tokens.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        validate() is called after all field-level validations pass.
        It's the right place to do cross-field or business logic checks.

        authenticate() is Django's built-in function that:
        1. Looks up the user by username
        2. Checks the password against the stored hash
        3. Returns the User object if valid, None if invalid
        """
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."}
            )

        # WHY RefreshToken?
        # RefreshToken.for_user(user) generates TWO tokens:
        #   - refresh token  : long-lived, used to get new access tokens
        #   - access token   : short-lived, sent with every API request
        #
        # The client stores BOTH. It uses the access token for requests.
        # When the access token expires, it uses the refresh token to get
        # a new access token WITHOUT asking the user to log in again.
        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        }


# ══════════════════════════════════════════════════════════════
# STUDENT PROFILE SERIALIZER
# Used by: GET/PUT /api/students/profile/
# ══════════════════════════════════════════════════════════════
class StudentProfileSerializer(serializers.ModelSerializer):
    """
    Serializes the StudentProfile model.

    Note: 'user' is read_only — the profile belongs to whoever
    is logged in. The student cannot set a different user_id.
    """
    # These fields come from the related User model
    # source='user.username' means: get username from the user FK
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["username", "email", "skills", "resume"]

    def validate_resume(self, value):
        """
        CUSTOM VALIDATION — Resume file size check.

        WHY CUSTOM VALIDATION?
        ─────────────────────────────────────────────
        Django doesn't limit file sizes by default.
        Without this check, a student could upload a 1GB file
        and crash the server. We limit resumes to 5MB max.

        How it works:
        - value.size gives file size in bytes
        - 5 * 1024 * 1024 = 5,242,880 bytes = 5MB
        ─────────────────────────────────────────────
        """
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if value and value.size > max_size:
            raise serializers.ValidationError(
                "Resume file too large. Maximum allowed size is 5MB."
            )
        return value


# ══════════════════════════════════════════════════════════════
# COMPANY PROFILE SERIALIZER
# Used by: GET/PUT /api/company/profile/
# ══════════════════════════════════════════════════════════════
class CompanyProfileSerializer(serializers.ModelSerializer):
    """
    Serializes the CompanyProfile model.
    """
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = CompanyProfile
        fields = ["username", "email", "company_name", "description"]
