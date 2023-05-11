from django.urls import path
from . import views

app_name = 'joejee'

urlpatterns = [
    path('', views.home, name="Home"),
    path('shop/',views.shop, name ="Shop"),
    path('contact/',views.contact, name ="Contact"),
    path('<slug:category_slug>',views.shop,name ="product_by_category"),
    path('<slug:category_slug>/<slug:product_slug>/',views.product_detail,name ="product_detail"),
    path('signin/',views.login,name='user_signin'),
    path('signup/',views.register,name='user_register'),
    
    path('dashboard/',views.dashboard,name='dashboard'),
    path('my_orders/',views.my_orders,name='my_orders'),
    path('order_details/<int:order_id>',views.orders_details,name='orders_details'),
    path('cancel_order/<int:order_id>',views.cancel_order,name='cancel_order'),
    path('change_password/',views.change_password,name='change_password'),
    path('my_addresses/',views.my_addresses,name='my_addresses'),
    path('my_addresses/add_address',views.save_address,name='add_address'),
    path('activate-address/',views.activate_address,name='activate-address'),
    path('search-products/',views.search_products,name='search_products'),
    
    
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('logout/',views.logout,name='user_logout'),
    path('verify/', views.verify_code,name='verify'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    
    
]