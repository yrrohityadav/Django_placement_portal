# applications/views.py

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application
from .serializers import (
    ApplicationSerializer,
    ApplySerializer,
    ApplicationStatusUpdateSerializer,
)
from users.permissions import IsStudent, IsCompany


# ══════════════════════════════════════════════════════════════
# APPLY FOR JOB
# Endpoint: POST /api/applications/
# Access:   Students only
# ══════════════════════════════════════════════════════════════
class ApplyJobAPIView(APIView):
    """
    Student applies to a job.

    The student's identity comes from request.user (JWT token).
    They only need to send the job_id in the request body.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        serializer = ApplySerializer(
            data=request.data,
            # We pass the student via context so the serializer
            # can use it in validate() without it being in the request body
            context={"student": request.user},
        )
        if serializer.is_valid(raise_exception=True):
            application = serializer.save()
            return Response(
                {
                    "message": "Application submitted successfully!",
                    "application": ApplicationSerializer(application).data,
                },
                status=status.HTTP_201_CREATED,
            )


# ══════════════════════════════════════════════════════════════
# STUDENT — VIEW OWN APPLICATIONS
# Endpoint: GET /api/applications/my/
# Access:   Students only
# ══════════════════════════════════════════════════════════════
class MyApplicationsAPIView(APIView):
    """
    Student views all their own job applications.

    Filter by status using query params:
    GET /api/applications/my/?status=pending
    GET /api/applications/my/?status=shortlisted
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        # Only get applications for the logged-in student
        applications = Application.objects.filter(student=request.user)

        # Optional filter: ?status=pending (or shortlisted / rejected)
        status_filter = request.query_params.get("status")
        if status_filter:
            applications = applications.filter(status=status_filter)

        serializer = ApplicationSerializer(applications, many=True)
        return Response(
            {
                "count": applications.count(),
                "applications": serializer.data,
            }
        )


# ══════════════════════════════════════════════════════════════
# COMPANY — VIEW APPLICATIONS FOR THEIR JOBS
# Endpoint: GET /api/applications/company/
# Access:   Companies only
# ══════════════════════════════════════════════════════════════
class CompanyApplicationsAPIView(APIView):
    """
    Company views all applications submitted to their job postings.

    Concept:
    - request.user is the logged-in company
    - We filter applications where the related job belongs to this company
    - job__company=request.user uses Django's double-underscore (__)
      to traverse the relationship: Application → Job → company field
    """
    permission_classes = [IsAuthenticated, IsCompany]

    def get(self, request):
        # job__company means: go to the 'job' FK, then look at its 'company' field
        applications = Application.objects.filter(job__company=request.user)

        # Optional filter by specific job
        job_id = request.query_params.get("job_id")
        if job_id:
            applications = applications.filter(job_id=job_id)

        # Optional filter by status
        status_filter = request.query_params.get("status")
        if status_filter:
            applications = applications.filter(status=status_filter)

        serializer = ApplicationSerializer(applications, many=True)
        return Response(
            {
                "count": applications.count(),
                "applications": serializer.data,
            }
        )


# ══════════════════════════════════════════════════════════════
# COMPANY — UPDATE APPLICATION STATUS
# Endpoint: PATCH /api/applications/<id>/status/
# Access:   Companies only (must own the job)
# ══════════════════════════════════════════════════════════════
class UpdateApplicationStatusAPIView(APIView):
    """
    Company updates the status of an application (shortlist/reject/select).

    WHY PATCH instead of PUT?
    ─────────────────────────────────────────────────────────────
    PUT   = replace the ENTIRE resource (send all fields)
    PATCH = update ONLY the fields you send (partial update)

    Since we're only changing 'status', PATCH is the right choice.
    ─────────────────────────────────────────────────────────────

    OWNERSHIP CHECK:
    We verify the application belongs to a job that THIS company owns.
    Company A cannot update application statuses for Company B's jobs.
    """
    permission_classes = [IsAuthenticated, IsCompany]

    def patch(self, request, pk):
        try:
            application = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response(
                {"error": f"Application with id {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Ownership check: does this application belong to this company's job?
        if application.job.company != request.user:
            return Response(
                {"error": "You can only update applications for your own job postings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ApplicationStatusUpdateSerializer(
            application, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": "Application status updated successfully.",
                    "application": ApplicationSerializer(application).data,
                }
            )
