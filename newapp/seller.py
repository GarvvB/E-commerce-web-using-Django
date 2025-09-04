from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, SellerRegisterForm
from .models import SellerProfile, Product

def seller_register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        seller_form = SellerRegisterForm(request.POST)
        if user_form.is_valid() and seller_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = 'seller'
            user.save()

            seller = seller_form.save(commit=False)
            seller.user = user
            seller.save()

            login(request, user)
            return redirect('sellerpage')
    else:
        user_form = UserRegisterForm()
        seller_form = SellerRegisterForm()
    return render(request, 'seller_register.html', {
        'user_form': user_form, 'seller_form': seller_form
    })

def sellerpage(request):
    return render(request, 'sellerpage.html')

def becomeseller(request):
    return render(request, 'becomeseller.html')

def sellerreg(request):
    return render(request,'sellerreq.html')