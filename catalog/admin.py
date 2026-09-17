from django.contrib import admin
from .models import Category, Brand, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "discount_price", "stock", "is_active")
    list_filter = ("category", "brand", "is_active")
    search_fields = ("name",)
    inlines = [ProductImageInline]
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Category)
admin.site.register(Brand)
