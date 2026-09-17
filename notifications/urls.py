from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("poll/", views.poll_notifications, name="poll"),
]
