from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from catalog.models import Product
from .cart import Cart
from .forms import CheckoutForm, OrderLookupForm
from .models import Order, OrderItem
from .services import check_repeat_ip_after_cancel
from notifications.services import notify_new_order


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    cart = Cart(request)
    cart.add(product, quantity=quantity)
    messages.success(request, f"Added {product.name} to cart.")
    return redirect(request.POST.get("next", "storefront:home"))


@require_POST
def cart_update(request, product_id):
    quantity = int(request.POST.get("quantity", 1))
    Cart(request).update(product_id, quantity)
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, product_id):
    Cart(request).remove(product_id)
    return redirect("orders:cart_detail")


def cart_detail(request):
    cart = Cart(request)
    return render(request, "storefront/cart.html", {"cart": cart})


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("storefront:home")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.ip_address = getattr(request, "visitor_ip", None)
                order.save()

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item["product"],
                        product_name=item["product"].name,
                        unit_price=item["product"].current_price,
                        quantity=item["quantity"],
                    )

            # These must run AFTER the order (and its IP) is committed.
            notify_new_order(order)
            check_repeat_ip_after_cancel(order)

            cart.clear()
            messages.success(request, f"Order placed! Your order number is {order.order_number}.")
            return redirect("orders:order_success", order_number=order.order_number)
    else:
        form = CheckoutForm()

    return render(request, "storefront/checkout.html", {"form": form, "cart": cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, "storefront/order_success.html", {"order": order})


def order_lookup(request):
    order = None
    form = OrderLookupForm(request.GET or None)
    if request.GET and form.is_valid():
        order = Order.objects.filter(
            phone=form.cleaned_data["phone"],
            order_number__iexact=form.cleaned_data["order_number"],
        ).first()
        if not order:
            messages.error(request, "No matching order found. Check your phone number and order number.")
    return render(request, "storefront/order_lookup.html", {"form": form, "order": order})


@require_POST
def order_cancel(request, order_number):
    """Customer-initiated cancellation from the lookup page.
    Marking it cancelled here is what makes it count for the
    'same IP re-orders after a cancellation' admin alert later.
    """
    order = get_object_or_404(Order, order_number=order_number)
    if order.status in (Order.Status.PENDING, Order.Status.PROCESSING):
        from django.utils import timezone
        order.status = Order.Status.CANCELLED
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at"])
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.error(request, "This order can no longer be cancelled.")
    return redirect("orders:order_lookup")
