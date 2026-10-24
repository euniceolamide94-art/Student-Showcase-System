from django import template
from django.contrib.auth.models import User
from accounts.models import StudentProfile, Project

register = template.Library()


@register.simple_tag
def total_users():
    return User.objects.count()


@register.simple_tag
def total_students():
    return StudentProfile.objects.count()


@register.simple_tag
def total_projects():
    return Project.objects.count()