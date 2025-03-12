from django.urls import path
from . import views
from .views import trainers_average_points

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Trainer-related URLs
    path("signup/trainer/", views.trainer_signup, name="trainer_signup"),
    path("trainer/dashboard/", views.trainer_dashboard, name="trainer_dashboard"),
    path("trainer/edit-profile/", views.edit_profile, name="edit_profile"),

    # Admin-related URLs
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/trainer/<int:trainer_id>/", views.trainer_detail, name="trainer_detail"),
    path("admin/edit_trainer/<int:trainer_id>/", views.edit_trainer, name="edit_trainer"),
    path("admin/delete_trainer/<int:trainer_id>/", views.delete_trainer, name="delete_trainer"),

    # Feedback-related URLs
    path("feedback/", views.feedback_list, name="feedback_list"),
    path("students-feedback/", views.students_feedback, name="students_feedback"),
    path('trainers-average/', trainers_average_points, name='trainers_average'),
]
