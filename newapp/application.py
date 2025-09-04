from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Sum, F
from django.views.decorators.http import require_POST
import json

from .forms import ProductForm, UserRegisterForm, SellerProfileForm, UserProfileForm
from .models import Product, SellerProfile, Order, OrderItem, Cart, CartItem

User = get_user_model()

# ---------------------------
# Home & static pages
# ---------------------------
def index(request):
    """Landing page showing all products + categories."""
    products = Product.objects.filter(is_available=True)
    types = products.values_list('product_type', flat=True).distinct()
    types = sorted(set(t.title() for t in types if t))
    return render(request, 'index.html', {'products': products, 'types': types})

def hotdealpage(request):
    """Hot deals page - could show discounted products."""
    hot_products = Product.objects.filter(is_available=True)[:8]  # Show first 8 products as hot deals
    return render(request, 'hotdeal.html', {'hot_products': hot_products})

def support(request):
    return render(request, 'support.html')

# ---------------------------
# Cart functionality
# ---------------------------
@login_required
def cart(request):
    """Display user's cart."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
@require_POST
def add_to_cart(request, product_id):
    """Add product to cart via AJAX."""
    try:
        product = get_object_or_404(Product, id=product_id, is_available=True)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')

# ---------------------------
# User Dashboard & Profile
# ---------------------------
@login_required
def buyer_dashboard(request):
    """Buyer dashboard with orders and profile management."""
    if request.user.role != 'buyer':
        return redirect('seller_dashboard')
    
    recent_orders = Order.objects.filter(buyer=request.user)[:5]
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items_count = CartItem.objects.filter(cart=cart).count()
    
    return render(request, 'buyer_dashboard.html', {
        'recent_orders': recent_orders,
        'cart_items_count': cart_items_count,
    })

@login_required
def account(request):
    """User account page - redirects to appropriate dashboard."""
    if request.user.role == 'seller':
        return redirect('seller_dashboard')
    else:
        return redirect('buyer_dashboard')

@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('buyer_dashboard')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def my_orders(request):
    """Display user's orders."""
    orders = Order.objects.filter(buyer=request.user)
    return render(request, 'my_orders.html', {'orders': orders})

# ---------------------------
# Helpers
# ---------------------------
def _unique_username_from(seed: str) -> str:
    """Create a slug-like username that's unique in the user table."""
    base = slugify(seed) or "seller"
    candidate = base
    i = 1
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base}{i}"
    return candidate

# ---------------------------
# Registration (buyer & seller)
# ---------------------------
def register(request):
    """Single registration view for both buyers and sellers."""
    if request.method == 'POST':
        role = request.POST.get('role', 'buyer')

        if role == 'seller':
            # Seller registration
            seller_form = SellerProfileForm(request.POST)
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()

            if not email or not password:
                messages.error(request, "Email and password are required for seller registration.")
                return render(request, 'registerpage.html', {
                    'user_form': UserRegisterForm(),
                    'seller_form': seller_form,
                    'selected_role': 'seller'
                })

            if seller_form.is_valid():
                shop_name = seller_form.cleaned_data.get('shop_name', '').strip()
                suggested = shop_name or email.split('@')[0]
                username = _unique_username_from(suggested)

                # Create user
                user = User(
                    username=username, 
                    email=email, 
                    role='seller',
                    first_name=first_name,
                    last_name=last_name
                )
                user.set_password(password)
                user.save()

                # Create seller profile
                SellerProfile.objects.create(
                    user=user,
                    shop_name=shop_name,
                    is_seller=True,
                    is_customer=False
                )

                login(request, user)
                messages.success(request, f'Welcome {shop_name}! Your seller account has been created.')
                return redirect('seller_dashboard')
            else:
                return render(request, 'registerpage.html', {
                    'user_form': UserRegisterForm(),
                    'seller_form': seller_form,
                    'selected_role': 'seller'
                })

        else:  # buyer registration
            user_form = UserRegisterForm(request.POST)
            seller_form = SellerProfileForm()

            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.role = 'buyer'
                user.save()
                
                # Create cart for new buyer
                Cart.objects.create(user=user)
                
                login(request, user)
                messages.success(request, f'Welcome {user.first_name}! Your account has been created.')
                return redirect('buyer_dashboard')

            return render(request, 'registerpage.html', {
                'user_form': user_form,
                'seller_form': seller_form,
                'selected_role': 'buyer'
            })

    # GET request
    return render(request, 'registerpage.html', {
        'user_form': UserRegisterForm(),
        'seller_form': SellerProfileForm(),
        'selected_role': 'buyer'
    })

# ---------------------------
# Auth (login / logout)
# ---------------------------
def user_login(request):
    """Login for both buyers and sellers."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.role == 'seller':
                return redirect('seller_dashboard')
            elif user.role == 'admin':
                return redirect('admin:index')
            else:
                return redirect('buyer_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'login.html')

# Keep compatibility
login_view = user_login

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

# ---------------------------
# Seller Dashboard & Management
# ---------------------------
@login_required
def seller_dashboard(request):
    """Seller dashboard with products and analytics."""
    if request.user.role != 'seller':
        messages.error(request, "You don't have seller permissions.")
        return redirect('buyer_dashboard')

    # Ensure seller profile exists
    try:
        seller_profile = request.user.sellerprofile
    except SellerProfile.DoesNotExist:
        messages.error(request, "Seller profile not found. Please contact support.")
        return redirect('index')

    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_value = sum(p.price * p.quantity for p in products)
    
    # Recent orders for seller's products
    recent_orders = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product')[:10]

    return render(request, 'seller_dashboard.html', {
        'products': products,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_value': total_value,
        'recent_orders': recent_orders,
        'seller_profile': seller_profile,
    })

# ---------------------------
# Product CRUD (seller only)
# ---------------------------
@login_required
def addproduct(request):
    """Add new product (seller only)."""
    if request.user.role != 'seller':
        messages.error(request, "Only sellers can add products.")
        return redirect('index')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    
    return render(request, 'addproduct.html', {'form': form})

@login_required
def showproduct(request):
    """Show seller's products."""
    if request.user.role != 'seller':
        messages.error(request, "Access denied.")
        return redirect('index')

    products = Product.objects.filter(seller=request.user)
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_value = sum(p.price * p.quantity for p in products)
    
    return render(request, 'showproduct.html', {
        'products': products,
        'total_quantity': total_quantity,
        'total_value': total_value
    })

@login_required
def updateproduct(request, product_id):
    """Update product (seller only)."""
    if request.user.role != 'seller':
        messages.error(request, "Access denied.")
        return redirect('index')

    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'updateproduct.html', {'form': form, 'product': product})

@login_required
def deleteproduct(request, product_id):
    """Delete product (seller only)."""
    if request.user.role != 'seller':
        messages.error(request, "Access denied.")
        return redirect('index')

    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('seller_dashboard')
    
    return render(request, 'deleteproduct.html', {'product': product})

# ---------------------------
# Product Detail & Purchase
# ---------------------------
def product_detail(request, product_id):
    """Product detail page."""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    related_products = Product.objects.filter(
        product_type=product.product_type,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

# ---------------------------
# Order Management
# ---------------------------
@login_required
def create_order(request):
    """Create order from cart."""
    if request.method == 'POST':
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            
            if not cart_items.exists():
                messages.error(request, 'Your cart is empty.')
                return redirect('cart')
            
            # Calculate total
            total_amount = sum(item.get_total_price() for item in cart_items)
            
            # Get shipping address from form
            shipping_address = request.POST.get('shipping_address', '')
            if not shipping_address:
                messages.error(request, 'Shipping address is required.')
                return redirect('cart')
            
            # Create order
            order = Order.objects.create(
                buyer=request.user,
                total_amount=total_amount,
                shipping_address=shipping_address
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product quantity
                product = cart_item.product
                if product.quantity >= cart_item.quantity:
                    product.quantity -= cart_item.quantity
                    product.save()
            
            # Clear cart
            cart_items.delete()
            
            messages.success(request, f'Order #{order.id} placed successfully!')
            return redirect('my_orders')
            
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
            return redirect('cart')
    
    return redirect('cart')

# ---------------------------
# Helpers
# ---------------------------
def _unique_username_from(seed: str) -> str:
    """Create a slug-like username that's unique in the user table."""
    base = slugify(seed) or "user"
    candidate = base
    i = 1
    while User.objects.filter(username=candidate).exists():
        i += 1
        candidate = f"{base}{i}"
    return candidate