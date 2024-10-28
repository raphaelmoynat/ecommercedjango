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
    if request.user.is_superuser:
        form = ProductForm()
        if request.method == 'POST':
            form = ProductForm(request.POST)
            if form.is_valid():
                product = form.save(commit=False)
                product.author = request.user
                product.save()
                return redirect('product')
        return render(request, 'website/add_product.html', {"form": form, 'btnValue': 'Ajouter'})
    else:
        return redirect('product')

def show_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'website/product_show.html', {
        'product': product,
    })


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_superuser:
        product.delete()
        return redirect('product')
    else:
        return redirect('product')

def update_product(request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.user.is_superuser:
            if request.method == 'POST':
                form = ProductForm(request.POST, instance=product)
                if form.is_valid():
                    form.save()
                    return redirect('show_product', article_id=product.id)
            else:
                form = ProductForm(instance=product)
            return render(request, 'website/add_product.html', {
                'form': form,
                'product': product,
                'btnValue': 'Modifier'
            })

        else:
            return redirect('product')


def add_to_cart(request, product_id):
    product_id = str(product_id)
    cart = request.session.get('cart', {})

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    request.session['cart'] = cart

    referer = request.META.get('HTTP_REFERER', '')
    if '/article/' in referer:
        return redirect('show_product', product_id=product_id)
    else:
        return redirect('view_cart')


def view_cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal

    return render(request, 'website/cart.html', {
        'cart': cart_items,
        'total': total,
    })


def remove_from_cart(request, product_id):
    product_id = str(product_id)
    cart = request.session.get('cart', {})
    if product_id in cart:
        if cart[product_id] > 1:
            cart[product_id] -= 1
        else:
            del cart[product_id]

    request.session['cart'] = cart
    return redirect('view_cart')

def remove_row(request, product_id):
    product_id = str(product_id)
    cart = request.session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
    request.session['cart'] = cart
    return redirect('view_cart')

def empty_cart(request):
    request.session['cart'] = {}
    return redirect('view_cart')

