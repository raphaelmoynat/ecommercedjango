from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404


from website.models import Product, Order, OrderItem

from website.forms import ProductForm, RegisterForm, LoginForm
from django.contrib.auth import authenticate, login, logout



import stripe
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone



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
    return redirect('product')

def add_product(request):
    if request.user.is_superuser:
        form = ProductForm()
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
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
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect('show_product', product_id=product.id)
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

def recap(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
        total += subtotal

    return render(request, 'website/recap.html', {
        'cart_items': cart_items,
        'total': total,
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

def confirm_order(request):
    if request.user.is_authenticated:
        cart = request.session.get('cart', {})
        order_items = []
        total_amount = 0

        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            subtotal = int(product.price * quantity * 100)
            order_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': product.name,
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': quantity,
            })
            total_amount += subtotal

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=order_items,
            mode='payment',
            success_url=request.build_absolute_uri('/order/success/'),
            cancel_url=request.build_absolute_uri('/recap/'),
        )

        return redirect(session.url, code=303)
    else:
        return redirect('product')

@csrf_exempt
def payment_success(request):
    cart = request.session.get('cart', {})
    total = 0
    order = Order.objects.create(user=request.user, total=total, date=timezone.now())

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        OrderItem.objects.create(order=order, product=product, quantity=quantity, subtotal=subtotal)
        total += subtotal
    order.total = total
    order.save()
    request.session['cart'] = {}

    return render(request, 'website/payment_success.html', {'order': order})

def order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'website/order.html', {'order': order})

def profile(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user)
        return render(request, 'website/profile.html', {'orders': orders})
    else:
        return redirect('product')


def all_orders(request):
    if request.user.is_superuser:
        orders = Order.objects.all()
        return render(request, 'website/all_orders.html', {'orders': orders})
    else:
        return redirect('product')



