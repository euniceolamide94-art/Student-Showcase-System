from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):

    DEPARTMENT_CHOICES = [
        ('Computer Science', 'Computer Science'),
        ('Software Engineering', 'Software Engineering'),
        ('Networking', 'Networking'),
    ]

    LEVEL_CHOICES = [
        ('ND1', 'ND1'),
        ('ND2', 'ND2'),
        ('HND1', 'HND1'),
        ('HND2', 'HND2'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100
    )

    matric_number = models.CharField(
        max_length=20,
        unique=True
    )

    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES
    )

    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES
    )

    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True
    )

    skills = models.CharField(
        max_length=255,
        blank=True
    )

    github_link = models.URLField(
        blank=True,
        null=True
    )

    linkedin_link = models.URLField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.full_name
    
class Project(models.Model):

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    title = models.CharField(
        max_length=100
    )

    description = models.TextField()

    technologies = models.CharField(
        max_length=255
    )

    project_image = models.ImageField(
        upload_to='project_images/',
        blank=True,
        null=True
    )

    github_link = models.URLField(
        blank=True,
        null=True
    )

    live_demo_link = models.URLField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title