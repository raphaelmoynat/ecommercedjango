from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from website.models import Product

from website.forms import ProductForm, RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout



# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def product(request):
    products = Product.objects.all()
    return render(request, 'website/products.html', {'products': products})

def user_register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'website/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('product')
    else:
        form = LoginForm()
    return render(request, 'website/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')

def add_product(request):
    if request.user.is_authenticated:
        form = ProductForm()
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save(commit=False)
                product.author = request.user
                product.save()
                return redirect('product')
        return render(request, 'website/add_product.html', {"form": form})
    else:
        return redirect('product')

def show_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'website/product_show.html', {
        'product': product,
    })
