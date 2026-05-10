# jobs/models.py

# WHY get_user_model() instead of importing User directly?
# ─────────────────────────────────────────────────────────────
# Django best practice: always use get_user_model() when
# referencing the user model in other apps.
#
# If you write: from users.models import User
# → Your app is tightly coupled to ONE specific User class
# → If you ever change AUTH_USER_MODEL, you'd break this file
#
# If you write: get_user_model()
# → Django resolves whatever is set as AUTH_USER_MODEL
# → Your code stays flexible and won't break on User model changes
# ─────────────────────────────────────────────────────────────

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Job(models.Model):
    # ForeignKey → one company can have MANY jobs
    # CASCADE → if the company user is deleted, all their jobs are deleted too
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    salary = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Default ordering: newest jobs appear first
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company.username}"