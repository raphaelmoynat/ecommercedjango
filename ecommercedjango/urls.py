"""
URL configuration for ecommercedjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('website/', views.index, name='index'),
    path('', views.product, name='product'),
    path('add/', views.add_product, name='add_product'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('article/<int:product_id>/', views.show_product, name='show_product'),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/edit/<int:product_id>/', views.update_product, name='update_product'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='app_cart_remove'),
    path('cart/remove_row/<int:product_id>/', views.remove_row, name='app_cart_remove_row'),
    path('cart/empty/', views.empty_cart, name='app_empty_cart'),
    path('recap/', views.recap, name='recap'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('order/<int:order_id>/', views.order, name='order'),
    path('order/success/', views.payment_success, name='payment_success'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.all_orders, name='all_orders'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
