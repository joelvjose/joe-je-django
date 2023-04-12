from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.Admin_home, name="Admin_Home"),
    
    path('customer', views.Admin_customer, name="customer_list"),
    path('customer/block/<int:id>/',views.block_customer, name='block_user'),
    path('customer/unblock/<int:id>/',views.unblock_customer, name='unblock_user'),
    # path('customer/add/',views.add_data_customer, name='add_customer'),
    
    path('Category', views.Admin_category, name="category_list"),
    path('Category/<int:id>/',views.update_category, name='update_category'),
    path('Category/delete/<int:id>/',views.delete_category, name='delete_category'),
    path('Category/add/',views.add_category, name='add_category'),
    
    path('products', views.Admin_product, name="product_list"),
    path('products/<int:id>/',views.update_product, name='update_product'),
    path('products/delete/<int:id>/',views.delete_product, name='delete_product'),
    path('products/add/',views.add_product, name='add_product'),
    
    path('variations', views.Admin_variation, name="variation_list"),
    path('variations/<int:id>/',views.update_variation, name='update_variation'),
    path('variations/delete/<int:id>/',views.delete_variation, name='delete_variation'),
    path('variations/add/',views.add_variation, name='add_variation'),
    
    # path('order', views.Admin_home, name="Admin_Home"),
    # path('banner', views.Admin_home, name="Admin_Home"),
    # path('coupon', views.Admin_home, name="Admin_Home"),
    
]