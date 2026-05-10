# placement_portal/urls.py
#
# This is the ROOT URL configuration.
# All app-level URLs are "included" here with a prefix.
# Django processes them in order, top to bottom.

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin panel (keep as-is)
    path("admin/", admin.site.urls),

    # All API routes — each app manages its own urls.py
    # 'api/' prefix means every endpoint starts with /api/
    path("api/", include("users.urls")),        # auth, profiles
    path("api/", include("jobs.urls")),         # job CRUD
    path("api/", include("applications.urls")), # applications
]

# ── MEDIA FILE SERVING (Development Only) ─────────────────────────────────
# In development, Django serves uploaded files (resumes) directly.
# When DEBUG=True, this adds a route: /media/<filename>
#
# In production, you'd use a web server (nginx/apache) to serve these.
# static() only activates when DEBUG=True — safe to keep here.
# ──────────────────────────────────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
