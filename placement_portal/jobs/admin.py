from django.contrib import admin
from .models import Job


class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "created_at")
    search_fields = ("title", "location")


admin.site.register(Job, JobAdmin)