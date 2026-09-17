from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "full_name", "phone", "ip_address", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "phone", "full_name", "ip_address")
    inlines = [OrderItemInline]
    readonly_fields = ("order_number", "ip_address", "created_at", "updated_at")
