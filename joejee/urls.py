from django.urls import path
from . import views

app_name = 'joejee'

urlpatterns = [
    path('', views.home, name="Home"),
    path('shop/',views.shop, name ="Shop"),
    path('<slug:category_slug>',views.shop,name ="product_by_category"),
    path('<slug:category_slug>/<slug:product_slug>/',views.product_detail,name ="product_detail"),
    path('signin/',views.login,name='user_signin'),
    path('signup/',views.register,name='user_register'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('logout/',views.logout,name='user_logout'),
    path('verify/', views.verify_code,name='verify'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
    path('resetpassword/',views.resetpassword,name='resetpassword'),
    
    
]