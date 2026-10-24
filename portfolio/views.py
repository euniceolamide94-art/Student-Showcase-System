
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import StudentProfileForm, ProjectForm
from .models import StudentProfile


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

    if request.method == "POST":
        logout(request)
        return redirect('login')

    return render(request, 'accounts/confirm_logout.html')


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

    projects = profile.projects.order_by('-created_at')

    return render(
        request,
        'accounts/dashboard.html',
        {
            'profile': profile,
            'projects': projects,
            'profile_complete': profile_is_complete(profile),
        }
    )


@login_required
def edit_profile(request):

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': '',
            'matric_number': f'PENDING-{request.user.pk}',
            'department': '',
            'level': ''
        }
    )

    if request.method == "POST":

        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            saved_profile = form.save(commit=False)

            if not saved_profile.matric_number.strip():
                form.add_error(
                    'matric_number',
                    'Please enter your matric number.'
                )
            else:
                saved_profile.user = request.user
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

    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': '',
            'matric_number': f'PENDING-{request.user.pk}',
            'department': '',
            'level': ''
        }
    )

    # Enforce the supervisor's requirement on the server.
    if not profile_is_complete(profile):
        messages.warning(
            request,
            "Please complete your student profile before adding a project."
        )
        return redirect('edit_profile')

    if request.method == "POST":

        form = ProjectForm(
            request.POST,
            request.FILES
        )

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
