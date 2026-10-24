from django.urls import path
from . import views


urlpatterns = [

    path(
        'register/',
        views.register,
        name='register'
    ),

    path(
        'login/',
        views.user_login,
        name='login'
    ),

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),
    
    path(
    'edit-profile/',
    views.edit_profile,
    name='edit_profile'
),

    path(
    'add-project/',
    views.add_project,
    name='add_project'
),
    
    path(
        'edit-project/<int:project_id>/',
        views.edit_project,
        name='edit_project'
    ),

path(
    'delete-project/<int:project_id>/',
    views.delete_project,
    name='delete_project'
),


    path(
        'showcase/',
        views.public_showcase,
        name='public_showcase'
    ),


    path(
        'student/<int:student_id>/',
        views.public_student_profile,
        name='public_student_profile'
    ),

path(
    'admin-dashboard/',
    views.admin_dashboard,
    name='admin_dashboard'
),

]