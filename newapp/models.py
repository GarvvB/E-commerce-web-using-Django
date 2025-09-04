from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin')
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

class SellerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    shop_name = models.CharField(max_length=100)

    def __str__(self):
        return self.shop_name or self.user.username
    
class Product(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # link to seller
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    product_type = models.CharField(max_length=255)
    image = models.ImageField(upload_to='products/')
    return_policy = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
