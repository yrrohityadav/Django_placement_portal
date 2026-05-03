from django.contrib import admin
from .models import User, StudentProfile, CompanyProfile


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff")
    list_filter = ("role",)
    search_fields = ("username", "email")


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "skills")


class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "company_name")


admin.site.register(User, UserAdmin)
admin.site.register(StudentProfile, StudentProfileAdmin)
admin.site.register(CompanyProfile, CompanyProfileAdmin)