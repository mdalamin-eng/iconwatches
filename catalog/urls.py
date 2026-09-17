from django.urls import path
from . import views

app_name = "storefront"

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
