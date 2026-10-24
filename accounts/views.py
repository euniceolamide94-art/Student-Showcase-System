from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .forms import StudentProfileForm, ProjectForm
from .models import StudentProfile, Project

def profile_is_complete(profile):
    return (
        bool(profile.full_name.strip())
        and bool(profile.matric_number.strip())
        and not profile.matric_number.startswith('PENDING-')
        and bool(profile.department)
        and bool(profile.level)
    )


def register(request):

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(request, user)

        messages.info(
            request,
            "Welcome! Please complete your student profile before adding a project."
        )

        return redirect('edit_profile')

    return render(request, 'accounts/register.html')


def user_login(request):

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            # Repair a missing profile for an existing user.
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': '',
                    'matric_number': f'PENDING-{user.pk}',
                    'department': '',
                    'level': ''
                }
            )

            login(request, user)

            return redirect('dashboard')

        messages.error(request, "Invalid login details.")

    return render(request, 'accounts/login.html')



@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('login')


@login_required
def dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': '',
            'matric_number': f'PENDING-{request.user.pk}',
            'department': '',
            'level': ''
        }
    )

    search_query = request.GET.get('q', '').strip()
    projects = profile.projects.order_by('-created_at')

    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(technologies__icontains=search_query) |
            Q(student__skills__icontains=search_query)
        )

    return render(
        request,
        'accounts/dashboard.html',
        {
            'profile': profile,
            'projects': projects,
            'profile_complete': profile_is_complete(profile),
            'search_query': search_query,
        }
    )


@login_required
def edit_profile(request):

    # Get the student's profile if one already exists.
    # Otherwise, leave profile as None.
    profile = getattr(request.user, 'studentprofile', None)

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            saved_profile = form.save(commit=False)
            saved_profile.user = request.user

            if not saved_profile.matric_number.strip():
                form.add_error(
                    'matric_number',
                    'Please enter your real matric number.'
                )
            else:
                saved_profile.save()

                if profile_is_complete(saved_profile):
                    messages.success(
                        request,
                        "Your profile has been completed successfully."
                    )
                    return redirect('dashboard')

                messages.error(
                    request,
                    "Please complete your name, matric number, department and level."
                )

    else:
        form = StudentProfileForm(instance=profile)

    return render(
        request,
        'accounts/edit_profile.html',
        {'form': form, 'profile': profile}
    )
    

@login_required
def add_project(request):
    profile = getattr(request.user, 'studentprofile', None)

    if profile is None or not profile_is_complete(profile):

     if not profile_is_complete(profile):
        messages.warning(
            request,
            "Please complete your student profile before adding a project."
        )
        return redirect('edit_profile')

    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)

        if form.is_valid():
            project = form.save(commit=False)
            project.student = profile
            project.save()

            messages.success(
                request,
                "Your project has been added successfully."
            )
            return redirect('dashboard')
    else:
        form = ProjectForm()

    return render(
        request,
        'accounts/add_project.html',
        {'form': form}
    )
    

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(
            request,
            "You are not authorised to access the administration dashboard."
        )
        return redirect('dashboard')

    total_users = User.objects.count()
    total_students = StudentProfile.objects.count()
    total_projects = Project.objects.count()

    recent_projects = Project.objects.select_related(
        'student'
    ).order_by('-created_at')[:5]

    return render(
        request,
        'accounts/admin_dashboard.html',
        {
            'total_users': total_users,
            'total_students': total_students,
            'total_projects': total_projects,
            'recent_projects': recent_projects,
        }
    )


@login_required
def edit_project(request, project_id):
    profile = getattr(request.user, 'studentprofile', None)

    if profile is None:
        messages.error(
            request,
            "Please complete your student profile first."
        )
        return redirect('edit_profile')

    project = Project.objects.filter(
        id=project_id,
        student=profile
    ).first()

    if project is None:
        messages.error(
            request,
            "Project not found or you do not have permission to edit it."
        )
        return redirect('dashboard')

    if request.method == "POST":
        form = ProjectForm(
            request.POST,
            request.FILES,
            instance=project
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your project has been updated successfully."
            )
            return redirect('dashboard')
    else:
        form = ProjectForm(instance=project)

 
    return render(
    request,
    'accounts/edit_project.html',
    {'form': form, 'project': project}
)
@login_required
def delete_project(request, project_id):
    if request.method != "POST":
        return redirect('dashboard')

    profile = getattr(request.user, 'studentprofile', None)

    if profile is None:
        messages.error(
            request,
            "Please complete your student profile first."
        )
        return redirect('dashboard')

    project = Project.objects.filter(
        id=project_id,
        student=profile
    ).first()

    if project is None:
        messages.error(
            request,
            "Project not found or you do not have permission to delete it."
        )
        return redirect('dashboard')

    project.delete()

    messages.success(
        request,
        "Your project has been deleted successfully."
    )

    return redirect('dashboard')



def public_showcase(request):
    search_query = request.GET.get('q', '').strip()
    department = request.GET.get('department', '').strip()
    level = request.GET.get('level', '').strip()

    projects = Project.objects.select_related(
        'student',
        'student__user'
    ).order_by('-created_at')

    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(technologies__icontains=search_query) |
            Q(student__skills__icontains=search_query) |
            Q(student__full_name__icontains=search_query) |
            Q(student__user__username__icontains=search_query)
        )

    if department:
        projects = projects.filter(
            student__department=department
        )

    if level:
        projects = projects.filter(
            student__level=level
        )

    return render(
        request,
        'accounts/public_showcase.html',
        {
            'projects': projects,
            'search_query': search_query,
            'selected_department': department,
            'selected_level': level,
        }
    )


def public_student_profile(request, student_id):
    student = get_object_or_404(
        StudentProfile,
        id=student_id
    )

    projects = student.projects.order_by('-created_at')

    return render(
        request,
        'accounts/public_student_profile.html',
        {
            'student': student,
            'projects': projects,
        }
    )
