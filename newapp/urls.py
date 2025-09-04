from django.urls import path, include
from . import application, seller  # make sure seller.py actually contains these views

urlpatterns = [
    path('index/', application.index, name='index'),
    path('cart/', application.cart, name='cart'),
    path('hotdeal/', application.hotdealpage, name='hotdeal'),
    path('support/', application.support, name='support'),
    path('account/', application.account, name='account'),

    # path('acctest/', include('django.contrib.auth.urls')), --> learn how to use this 

    # Authentication & dashboard
    path('register/', application.register, name='register'),
    path('login/', application.login_view, name='login'),
    path('buyer/dashboard/', application.buyer_dashboard, name='buyer_dashboard'),
    path('seller/dashboard', application.seller_dashboard, name='seller_dashboard'),

    # Product management
    path('addproduct/', application.addproduct, name='addproduct'),
    path('showproduct/', application.showproduct, name='showproduct'),
    path('updateproduct/<str:product_id>/', application.updateproduct, name='updateproduct'),
    path('deleteproduct/<str:product_id>/', application.deleteproduct, name='deleteproduct'),

    # Seller-specific
    path('becomeseller/', seller.becomeseller, name='becomeseller'),
    # path('sellerreq/', seller.sellerreg, name='sellerreq'),
    path('seller/', seller.sellerpage, name='sellerpage'),  # Make sure this exists in seller.py
    path('seller/register', seller.seller_register, name='seller_register'),
    path('seller/dashboard', seller.sellerpage, name='sellerpage'),
    path('logout/', application.user_logout, name='logout'),   
]
