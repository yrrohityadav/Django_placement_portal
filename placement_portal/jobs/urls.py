# jobs/urls.py

from django.urls import path
from .views import JobListCreateAPIView, JobDetailAPIView

urlpatterns = [
    # GET  /api/jobs/     → list all jobs (public)
    # POST /api/jobs/     → create a job (company only)
    path("jobs/", JobListCreateAPIView.as_view(), name="job-list-create"),

    # GET    /api/jobs/<id>/  → view single job (public)
    # PUT    /api/jobs/<id>/  → update job (owner company only)
    # DELETE /api/jobs/<id>/  → delete job (owner company only)
    path("jobs/<int:pk>/", JobDetailAPIView.as_view(), name="job-detail"),
]