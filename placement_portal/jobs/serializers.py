# jobs/serializers.py

from rest_framework import serializers
from .models import Job


# ══════════════════════════════════════════════════════════════
# JOB READ SERIALIZER
# Used to FORMAT jobs when sending them to the client (GET requests)
# ══════════════════════════════════════════════════════════════
class JobSerializer(serializers.ModelSerializer):
    """
    Converts a Job database object into JSON for API responses.

    We add 'company_name' and 'company_username' as extra read-only
    fields so the client doesn't just see a company ID — they see
    the actual company name.

    SerializerMethodField lets us compute a value with a method.
    """

    # source='company.username' → navigates the FK to get username
    company_username = serializers.CharField(
        source="company.username", read_only=True
    )

    # For the company name, we need to navigate: job → company user → profile
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "location",
            "salary",
            "company_username",
            "company_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "company_username", "company_name"]

    def get_company_name(self, obj):
        """
        get_<fieldname>() is automatically called by SerializerMethodField.
        obj = the Job instance being serialized.

        We try to get the company's profile. If it doesn't exist,
        we fall back to the username.
        """
        try:
            return obj.company.companyprofile.company_name
        except Exception:
            return obj.company.username


# ══════════════════════════════════════════════════════════════
# JOB CREATE/UPDATE SERIALIZER
# Used when company creates or edits a job (POST, PUT requests)
# ══════════════════════════════════════════════════════════════
class JobCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Handles job creation and update.

    Notice: 'company' is NOT in the fields list.
    The company is always taken from request.user in the view.
    This prevents a company from posting a job on behalf of
    another company by sending a different company_id.
    """

    class Meta:
        model = Job
        fields = ["title", "description", "location", "salary"]

    def validate_salary(self, value):
        """
        Custom validation: salary cannot be negative.
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("Salary cannot be negative.")
        return value
