# newapp/forms.py
from django import forms
from django.contrib.auth import get_user_model
from .models import Product, SellerProfile

User = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['seller']

# Buyer registration: username + email + password
class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# Seller registration: shop_name + email + password (separate from the User model)
# We use a regular Form to ensure shop_name doesn't end up in CustomUser by accident.
class SellerRegisterForm(forms.Form):
    shop_name = forms.CharField(max_length=100, label="Shop name")
    email = forms.EmailField(label="Email address")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
