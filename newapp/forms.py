from django import forms
from django.contrib.auth import get_user_model
from .models import Product, SellerProfile

User = get_user_model()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['seller']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Product Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Available Quantity'}),
            'product_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Electronics, Clothing'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'return_policy': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days return'}),
        }

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['shop_name']
        widgets = {
            'shop_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Shop Name'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }