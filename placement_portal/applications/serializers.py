# applications/serializers.py

from rest_framework import serializers
from .models import Application
from jobs.models import Job


# ══════════════════════════════════════════════════════════════
# APPLICATION READ SERIALIZER
# Used for GET responses — shows rich info about each application
# ══════════════════════════════════════════════════════════════
class ApplicationSerializer(serializers.ModelSerializer):
    """
    Converts Application objects to JSON for GET responses.
    Adds human-readable names instead of just IDs.
    """
    student_username = serializers.CharField(
        source="student.username", read_only=True
    )
    job_title = serializers.CharField(
        source="job.title", read_only=True
    )
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "student_username",
            "job_title",
            "company_name",
            "status",
            "applied_at",
        ]
        read_only_fields = fields  # This serializer is READ-ONLY

    def get_company_name(self, obj):
        """Get the company name from the job's company profile."""
        try:
            return obj.job.company.companyprofile.company_name
        except Exception:
            return obj.job.company.username


# ══════════════════════════════════════════════════════════════
# APPLY SERIALIZER
# Used for POST /api/applications/ — student applies to a job
# ══════════════════════════════════════════════════════════════
class ApplySerializer(serializers.Serializer):
    """
    Handles job application submission.

    We only need the job_id in the request body.
    The student is always taken from request.user (JWT token).

    WHY Serializer (not ModelSerializer)?
    We're doing custom logic, not directly mapping fields to the model.
    The student field is injected by the view, not provided by the client.
    """
    job_id = serializers.IntegerField()

    def validate_job_id(self, value):
        """Check that the job actually exists."""
        if not Job.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                f"Job with id {value} does not exist."
            )
        return value

    def validate(self, data):
        """
        Cross-field validation: check for duplicate application.

        WHY CUSTOM VALIDATION HERE?
        ─────────────────────────────────────────────────────────────
        The database has unique_together = ('student', 'job'), which
        will raise an IntegrityError if a student applies twice.

        But a raw IntegrityError returns an ugly 500 error to the client.
        By checking BEFORE saving, we return a clean 400 error instead:
        { "error": "You have already applied to this job." }

        This is one of the most important reasons for custom validation —
        converting database errors into friendly user-facing messages.
        ─────────────────────────────────────────────────────────────
        """
        student = self.context.get("student")
        job_id = data.get("job_id")

        if student and Application.objects.filter(
            student=student, job_id=job_id
        ).exists():
            raise serializers.ValidationError(
                {"detail": "You have already applied to this job."}
            )
        return data

    def create(self, validated_data):
        """Create the Application record."""
        student = self.context["student"]
        job = Job.objects.get(id=validated_data["job_id"])
        return Application.objects.create(student=student, job=job)


# ══════════════════════════════════════════════════════════════
# STATUS UPDATE SERIALIZER
# Used for PATCH /api/applications/<id>/status/
# Company updates application status (shortlisted, rejected, etc.)
# ══════════════════════════════════════════════════════════════
class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Only allows updating the 'status' field.
    All other fields are ignored — this is important for security.
    """
    class Meta:
        model = Application
        fields = ["status"]

    def validate_status(self, value):
        """Ensure the status is one of the allowed choices."""
        allowed = [choice[0] for choice in Application.STATUS_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Invalid status. Allowed values: {allowed}"
            )
        return value
