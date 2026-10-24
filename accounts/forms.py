from django import forms
from .models import StudentProfile, Project


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'full_name',
            'matric_number',
            'department',
            'level',
            'profile_picture',
            'bio',
            'skills',
            'github_link',
            'linkedin_link',
        ]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'technologies',
            'project_image',
            'github_link',
            'live_demo_link',
        ]

