from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "address", "city", "note"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 017XXXXXXXX"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Full delivery address"}),
            "city": forms.TextInput(attrs={"class": "form-control", "placeholder": "City"}),
            "note": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Order note (optional)"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = "".join(ch for ch in phone if ch.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError("Please enter a valid phone number.")
        return phone


class OrderLookupForm(forms.Form):
    """Customer looks up their own order(s). We deliberately require BOTH
    the phone number AND the order number - phone alone is too easy to
    guess/enumerate and would leak other customers' orders/addresses.
    """
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number used at checkout"}),
    )
    order_number = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Order number (from SMS/receipt)"}),
    )
