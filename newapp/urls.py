from django.urls import path
from . import application, seller

urlpatterns = [
    # Home and static pages
    path('', application.index, name='index'),
    path('index/', application.index, name='index'),
    path('hotdeal/', application.hotdealpage, name='hotdeal'),
    path('support/', application.support, name='support'),
    
    # Authentication
    path('register/', application.register, name='register'),
    path('login/', application.user_login, name='login'),
    path('logout/', application.user_logout, name='logout'),
    
    # User dashboards
    path('account/', application.account, name='account'),
    path('buyer/dashboard/', application.buyer_dashboard, name='buyer_dashboard'),
    path('seller/dashboard/', application.seller_dashboard, name='seller_dashboard'),
    
    # User profile management
    path('profile/edit/', application.edit_profile, name='edit_profile'),
    path('orders/', application.my_orders, name='my_orders'),
    
    # Cart functionality
    path('cart/', application.cart, name='cart'),
    path('cart/add/<int:product_id>/', application.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', application.remove_from_cart, name='remove_from_cart'),
    path('order/create/', application.create_order, name='create_order'),
    
    # Product management (seller only)
    path('product/add/', application.addproduct, name='addproduct'),
    path('products/', application.showproduct, name='showproduct'),
    path('product/update/<int:product_id>/', application.updateproduct, name='updateproduct'),
    path('product/delete/<int:product_id>/', application.deleteproduct, name='deleteproduct'),
    path('product/<int:product_id>/', application.product_detail, name='product_detail'),
    
    # Seller pages
    path('becomeseller/', seller.becomeseller, name='becomeseller'),
    path('seller/', seller.sellerpage, name='sellerpage'),
]