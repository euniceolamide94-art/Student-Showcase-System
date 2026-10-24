
from django.contrib import admin
from .models import StudentProfile, Project


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'matric_number',
        'user',
        'student_email',
        'department',
        'level',
    )

    search_fields = (
        'full_name',
        'matric_number',
        'user__username',
        'user__email',
    )

    list_filter = (
        'department',
        'level',
    )

    ordering = ('full_name',)

    @admin.display(description='Email')
    def student_email(self, obj):
     return obj.user.email


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'student',
        'created_at',
        'github_status',
        'live_demo_status',
    )

    search_fields = (
        'title',
        'student__full_name',
        'student__matric_number',
        'technologies',
    )

    list_filter = ('created_at',)

    ordering = ('-created_at',)

    @admin.display(description='GitHub Link')
    def github_status(self, obj):
        return 'Available' if obj.github_link else 'Not provided'

    @admin.display(description='Live Demo')
    def live_demo_status(self, obj):
        return 'Available' if obj.live_demo_link else 'Not provided'
