# jobs/views.py
#
# HOW PERMISSIONS WORK IN VIEWS:
# ─────────────────────────────────────────────────────────────
# permission_classes is a list of "guards" that DRF checks
# BEFORE running get(), post(), put(), delete().
#
# If ANY permission class returns False → DRF stops the request
# and returns:
#   - 401 Unauthorized (if user is not logged in)
#   - 403 Forbidden    (if user is logged in but lacks role/access)
#
# Order matters: IsAuthenticated first, then role checks.
# ─────────────────────────────────────────────────────────────

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job
from .serializers import JobSerializer, JobCreateUpdateSerializer
from users.permissions import IsCompany


# ══════════════════════════════════════════════════════════════
# JOB LIST + CREATE VIEW
# GET  /api/jobs/  → Anyone (even unauthenticated) can list jobs
# POST /api/jobs/  → Only authenticated companies can create jobs
# ══════════════════════════════════════════════════════════════
class JobListCreateAPIView(APIView):

    def get_permissions(self):
        """
        get_permissions() lets us set DIFFERENT permissions for
        different HTTP methods in the SAME view.

        GET  → AllowAny (public job board)
        POST → IsAuthenticated + IsCompany (protected)
        """
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsCompany()]

    def get(self, request):
        """
        List all jobs. Public endpoint — no auth needed.
        Students, companies, and guests can all browse jobs.
        """
        jobs = Job.objects.all()  # already ordered by -created_at (model Meta)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Company creates a new job.

        IMPORTANT: We do NOT accept 'company' in the request body.
        We always use request.user. This means a company can ONLY
        post jobs under their own account.
        """
        serializer = JobCreateUpdateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Pass the logged-in company user as 'company' argument
            job = serializer.save(company=request.user)
            return Response(
                {
                    "message": "Job created successfully.",
                    "job": JobSerializer(job).data,
                },
                status=status.HTTP_201_CREATED,
            )


# ══════════════════════════════════════════════════════════════
# JOB DETAIL VIEW (Single Job)
# GET    /api/jobs/<id>/  → Anyone can view a single job
# PUT    /api/jobs/<id>/  → Only the company that OWNS this job
# DELETE /api/jobs/<id>/  → Only the company that OWNS this job
# ══════════════════════════════════════════════════════════════
class JobDetailAPIView(APIView):

    def get_permissions(self):
        """
        GET is public. PUT and DELETE require company authentication.
        """
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated(), IsCompany()]

    def _get_job_or_404(self, pk):
        """
        Helper method: get a job by primary key (id).
        Returns the Job object OR raises a 404-style response dict.

        WHY a helper method?
        We use this in get(), put(), and delete() — instead of
        writing the same try/except block 3 times, we write it once.
        DRY principle: Don't Repeat Yourself.
        """
        try:
            return Job.objects.get(pk=pk)
        except Job.DoesNotExist:
            return None

    def get(self, request, pk):
        """View details of a single job."""
        job = self._get_job_or_404(pk)
        if not job:
            return Response(
                {"error": f"Job with id {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = JobSerializer(job)
        return Response(serializer.data)

    def put(self, request, pk):
        """
        Update a job.

        OWNERSHIP CHECK: Even though IsCompany ensures the user is
        a company, we also check that this specific company OWNS
        this specific job. Company A cannot edit Company B's jobs.

        job.company == request.user compares the FK relationship.
        """
        job = self._get_job_or_404(pk)
        if not job:
            return Response(
                {"error": f"Job with id {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Object-level permission check
        if job.company != request.user:
            return Response(
                {"error": "You can only edit your own job postings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = JobCreateUpdateSerializer(job, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            job = serializer.save()
            return Response(
                {
                    "message": "Job updated successfully.",
                    "job": JobSerializer(job).data,
                }
            )

    def delete(self, request, pk):
        """
        Delete a job.
        Same ownership check as put().
        """
        job = self._get_job_or_404(pk)
        if not job:
            return Response(
                {"error": f"Job with id {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if job.company != request.user:
            return Response(
                {"error": "You can only delete your own job postings."},
                status=status.HTTP_403_FORBIDDEN,
            )

        job_title = job.title
        job.delete()
        return Response(
            {"message": f"Job '{job_title}' deleted successfully."},
            status=status.HTTP_200_OK,
        )
