# applications/models.py

from django.contrib.auth import get_user_model  # Best practice
from django.db import models
from jobs.models import Job

User = get_user_model()


class Application(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),          # Just applied, no decision yet
        ("shortlisted", "Shortlisted"),  # Company is interested
        ("rejected", "Rejected"),        # Not selected
        ("selected", "Selected"),        # Got the job!
    )

    # ForeignKey to User (student)
    # related_name='applications' → lets us do student.applications.all()
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )

    # ForeignKey to Job
    # related_name='applications' → lets us do job.applications.all()
    job = models.ForeignKey(
        Job, on_delete=models.CASCADE, related_name="applications"
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # unique_together prevents duplicate applications at the DATABASE level.
        # Even if our Python code has a bug, the DB will still reject duplicates.
        unique_together = ("student", "job")
        ordering = ["-applied_at"]  # newest applications first

    def __str__(self):
        return f"{self.student.username} → {self.job.title} [{self.status}]"
