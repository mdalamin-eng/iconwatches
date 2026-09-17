from decimal import Decimal
from catalog.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    """Session-backed cart. Works for anonymous visitors - no account needed.
    Session data shape: {"<product_id>": {"quantity": int}}
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        pid = str(product.id)
        if pid in self.cart:
            self.cart[pid]["quantity"] += quantity
        else:
            self.cart[pid] = {"quantity": quantity}
        self.save()

    def update(self, product_id, quantity):
        pid = str(product_id)
        if pid in self.cart:
            if quantity <= 0:
                del self.cart[pid]
            else:
                self.cart[pid]["quantity"] = quantity
            self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(p.id): p for p in products}
        for pid, item in self.cart.items():
            product = products_map.get(pid)
            if not product:
                continue
            yield {
                "product": product,
                "quantity": item["quantity"],
                "subtotal": product.current_price * item["quantity"],
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    @property
    def total(self):
        return sum(Decimal(item["subtotal"]) for item in self)
