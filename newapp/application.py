from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify

from .forms import ProductForm, UserRegisterForm, SellerProfileForm
from .models import Product, SellerProfile

User = get_user_model()


# ---------------------------
# Home & static pages
# ---------------------------
def index(request):
    """Landing page showing all products + categories."""
    products = Product.objects.all()
    types = products.values_list('product_type', flat=True).distinct()
    types = sorted(set(t.title() for t in types))
    return render(request, 'index.html', {'products': products, 'types': types})


@login_required
def cart(request):
    return render(request, 'cart.html')


def hotdealpage(request):
    return render(request, 'hotdeal.html')


def support(request):
    return render(request, 'support.html')


@login_required
def account(request):
    """User account (buyer) summary page. Keeps the existing account.html usage."""
    return render(request, 'account.html')


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
    """
    Single registration view:
      - Buyer flow: expects username, email, password (UserRegisterForm)
      - Seller flow: expects shop_name (SellerProfileForm) + email & password in POST.
    Template should include a radio/select named 'role' with values 'buyer' or 'seller'.
    """
    if request.method == 'POST':
        role = request.POST.get('role', 'buyer')

        if role == 'seller':
            # seller_form handles seller-specific fields (shop_name).
            seller_form = SellerProfileForm(request.POST)
            # email + password are expected in POST (names: 'email', 'password')
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')

            if not email or not password:
                # keep user-friendly message and re-render
                messages.error(request, "Seller registration requires email and password.")
                return render(request, 'registerpage.html', {
                    'user_form': UserRegisterForm(),
                    'seller_form': seller_form,
                    'selected_role': 'seller'
                })

            if seller_form.is_valid():
                shop_name = seller_form.cleaned_data.get('shop_name', '').strip()
                # make a unique username based on shop_name or email prefix
                suggested = shop_name or email.split('@')[0]
                username = _unique_username_from(suggested)

                # create user
                user = User(username=username, email=email, role='seller')
                user.set_password(password)
                user.save()

                # create seller profile
                SellerProfile.objects.create(
                    user=user,
                    shop_name=shop_name,
                    is_seller=True,
                    is_customer=False
                )

                login(request, user)
                return redirect('seller_dashboard')
            else:
                # invalid seller form
                return render(request, 'registerpage.html', {
                    'user_form': UserRegisterForm(),
                    'seller_form': seller_form,
                    'selected_role': 'seller'
                })

        else:  # buyer flow
            user_form = UserRegisterForm(request.POST)
            seller_form = SellerProfileForm()  # blank for template rendering

            if user_form.is_valid():
                user = user_form.save(commit=False)
                user.set_password(user_form.cleaned_data['password'])
                user.role = 'buyer'
                user.save()
                login(request, user)
                return redirect('buyer_dashboard')

            # invalid buyer form -> re-render
            return render(request, 'registerpage.html', {
                'user_form': user_form,
                'seller_form': seller_form,
                'selected_role': 'buyer'
            })

    # GET request -> show both forms (template decides which inputs to show)
    return render(request, 'registerpage.html', {
        'user_form': UserRegisterForm(),
        'seller_form': SellerProfileForm(),
        'selected_role': 'buyer'
    })


# ---------------------------
# Auth (login / logout)
# ---------------------------
def user_login(request):
    """Login shared by buyer/seller/admin. Redirects based on role."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # redirect based on role
            if getattr(user, 'role', 'buyer') == 'seller':
                return redirect('seller_dashboard')
            elif getattr(user, 'role', 'buyer') == 'admin':
                return redirect('admin:index')
            else:
                return redirect('buyer_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


# keep old import compatibility: urls that reference `login_view` will still work
login_view = user_login


def user_logout(request):
    logout(request)
    return redirect('login')


# ---------------------------
# Dashboards
# ---------------------------
@login_required
def buyer_dashboard(request):
    # We reuse account.html as the buyer dashboard
    return render(request, 'account.html')


@login_required
def seller_dashboard(request):
    # only seller role should access
    if getattr(request.user, 'role', '') != 'seller':
        return HttpResponse("You are not authorized to view this page.", status=403)

    # ensure sellerprofile exists
    if not hasattr(request.user, 'sellerprofile'):
        return HttpResponse("Seller profile not found. Please contact support.", status=404)

    products = Product.objects.filter(seller=request.user)
    total_quantity = sum(p.quantity for p in products)
    total_value = sum(p.price * p.quantity for p in products)

    return render(request, 'sellerpage.html', {
        'products': products,
        'total_quantity': total_quantity,
        'total_value': total_value,
    })


# ---------------------------
# Product CRUD (seller only)
# ---------------------------
@login_required
def addproduct(request):
    if getattr(request.user, 'role', '') != 'seller':
        return HttpResponse("Unauthorized", status=403)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('showproduct')
    else:
        form = ProductForm()
    return render(request, 'addproduct.html', {'form': form})


@login_required
def showproduct(request):
    if getattr(request.user, 'role', '') != 'seller':
        return HttpResponse("Unauthorized", status=403)

    products = Product.objects.filter(seller=request.user)
    total_quantity = sum(p.quantity for p in products)
    total_value = sum(p.price * p.quantity for p in products)
    return render(request, 'showproduct.html', {
        'products': products,
        'total_quantity': total_quantity,
        'total_value': total_value
    })


@login_required
def updateproduct(request, product_id):
    if getattr(request.user, 'role', '') != 'seller':
        return HttpResponse("Unauthorized", status=403)

    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('showproduct')
    else:
        form = ProductForm(instance=product)
    return render(request, 'updateproduct.html', {'form': form, 'product': product})


@login_required
def deleteproduct(request, product_id):
    if getattr(request.user, 'role', '') != 'seller':
        return HttpResponse("Unauthorized", status=403)

    product = get_object_or_404(Product, pk=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('showproduct')
    return render(request, 'deleteproduct.html', {'product': product})
