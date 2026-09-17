from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product, Category
from notifications.services import notify_product_viewed


def home(request):
    products = Product.objects.filter(is_active=True)

    category_slug = request.GET.get("category")
    if category_slug:
        products = products.filter(category__slug=category_slug)

    q = request.GET.get("q")
    if q:
        products = products.filter(name__icontains=q)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.all()
    return render(request, "storefront/home.html", {
        "page_obj": page_obj,
        "categories": categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Fire an in-app notification event for admin/manager dashboards.
    # This is what the polling endpoint in `notifications` will surface.
    ip = getattr(request, "visitor_ip", None)
    notify_product_viewed(product=product, ip_address=ip)

    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "storefront/product_detail.html", {
        "product": product,
        "related": related,
    })
