# applications/urls.py

from django.urls import path
from .views import (
    ApplyJobAPIView,
    MyApplicationsAPIView,
    CompanyApplicationsAPIView,
    UpdateApplicationStatusAPIView,
)

urlpatterns = [
    # POST /api/applications/         → Student applies to a job
    # Body: { "job_id": 1 }
    path("applications/", ApplyJobAPIView.as_view(), name="apply-job"),

    # GET  /api/applications/my/      → Student sees own applications
    # Optional: ?status=pending
    path("applications/my/", MyApplicationsAPIView.as_view(), name="my-applications"),

    # GET  /api/applications/company/ → Company sees applications for its jobs
    # Optional: ?job_id=1 or ?status=shortlisted
    path("applications/company/", CompanyApplicationsAPIView.as_view(), name="company-applications"),

    # PATCH /api/applications/<id>/status/ → Company updates application status
    # Body: { "status": "shortlisted" }
    path(
        "applications/<int:pk>/status/",
        UpdateApplicationStatusAPIView.as_view(),
        name="update-application-status",
    ),
]
