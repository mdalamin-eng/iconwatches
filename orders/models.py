from django.db import models
from django.utils.crypto import get_random_string
from catalog.models import Product


def generate_order_number():
    return get_random_string(10, allowed_chars="0123456789ABCDEFGHJKMNPQRSTVWXYZ")


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    order_number = models.CharField(max_length=12, unique=True, default=generate_order_number, editable=False)

    # Guest checkout fields - no account required
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, db_index=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number} ({self.phone})"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot, in case product changes/deleted later
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
