from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<str:order_number>/status/", views.order_update_status, name="order_update_status"),
    path("settings/notifications/", views.notification_settings, name="notification_settings"),
]
