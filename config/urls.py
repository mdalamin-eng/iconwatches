from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("django-admin/", admin.site.urls),  # built-in admin, kept separate from our own dashboard
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("orders/", include("orders.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("", include("catalog.urls")),  # storefront lives at root
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
