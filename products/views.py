import json
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect
from joejee.models import Account
from .models import category,Product,Images,Variation,Coupon
from orders.models import Order,OrderProduct
from .forms import AccountForm,ProductForm,CategoryForm,ImagesForm,VariationForm,CouponForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from datetime import datetime,timedelta
from django.core import serializers
from django.utils import timezone

# Create your views here.
from django.shortcuts import render

@login_required(login_url='joejee:user_signin')
def Admin_home(request):
    orders = Order.objects.all().order_by('-created_at')[:5]
    # ordered_product = OrderProduct.objects.all().order_by('-created_at')[:5]
    products = Product.objects.all().order_by('-id')
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    
    dates = [start_of_week + timedelta(days=i) for i in range(7)]

    sales = []
    for date in dates:
        Orders = OrderProduct.objects.filter(
            ordered=True,
            created_at__year=date.year,
            created_at__month=date.month,
            created_at__day=date.day,
        )
        total_sales = sum(order.product_price * order.quantity for order in Orders)
        sales.append(total_sales)
    context = {
        'orders': orders,
        # 'ordered_product':ordered_product,
        'products':products,
        'dates':dates,
        'sales':sales,
    }
    return render(request,'products/index.html',context)

def add_order_filter(request):
    body = json.loads(request.body)
    try:
        start_date =datetime.strptime(body['from'],'%Y-%m-%d')
        end_date = datetime.strptime(body['to'],'%Y-%m-%d')
    except ValueError:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=end_date.weekday())
    try:
        orders = Order.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        json_data = serializers.serialize('json', orders)
    except Order.DoesNotExist:
        orders = None     
    data ={
             "order":json_data,
            }
    return JsonResponse(data)
# ============================================================================================
# ====================================== CUSTOMER PANEL ======================================
@login_required(login_url='joejee:user_signin')
def Admin_customer(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(first_name__icontains = q)|Q(email__icontains = q)|Q(phone_number__icontains = q))
        users = Account.objects.filter(multiple_q,is_superadmin=False).order_by('id').reverse()
    else:
        users = Account.objects.filter(is_superadmin=False).order_by('id').reverse()
    context = {
        'users': users,
    }
    return render(request,'products/customer.html',context)

# -====================== customer add,edit and update data===========================
@login_required(login_url='joejee:user_signin')
def unblock_customer(request,id):
    if request.method == 'POST':
        pi = Account.objects.get(pk=id)
        pi.is_active=True
        pi.save()
        return HttpResponseRedirect('/admin/customer')
    

@login_required(login_url='joejee:user_signin')
def block_customer(request,id):
    if request.method == 'POST':
        pi = Account.objects.get(pk=id)
        pi.is_active=False
        pi.save()
        return HttpResponseRedirect('/admin/customer')
    # else:
    #     pi = Account.objects.get(pk=id)
    #     fm = AccountForm( instance=pi)
    # return render(request, 'products/update_customer.html',{'form':fm})

# =========end of============== customer add,edit and update data ============================
# ====================================== CUSTOMER PANEL ======================================


# =============================================================================================
# ====================================== CATEGORY ============================================
@login_required(login_url='joejee:user_signin')
def Admin_category(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(cat_name__icontains = q))
        cat = category.objects.filter(multiple_q)
    else:
        cat = category.objects.all()
    context = {
        'category': cat,
    }
    return render(request,'products/category.html',context)

@login_required(login_url='joejee:user_signin')
def delete_category(request,id):
    if request.method == 'POST':
        pi = category.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/Category')
    

@login_required(login_url='joejee:user_signin')
def update_category(request,id):
    if request.method == 'POST':
        pi = category.objects.get(pk=id)
        fm = CategoryForm(request.POST, instance=pi)
        if fm.is_valid:
            fm.save()
        return HttpResponseRedirect('/admin/Category')
    else:
        pi = category.objects.get(pk=id)
        fm = CategoryForm( instance=pi)
    return render(request, 'products/update_category.html',{'form':fm})

@login_required(login_url='joejee:user_signin')
def add_category(request):
    if request.method == 'POST' :
        form = CategoryForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect('/admin/Category')
            form = CategoryForm()
    else:
        form = CategoryForm()
    return render(request, 'products/add_category.html',{'form':form})

# ====================================== CATEGORY ============================================
# =============================================================================================

# =============================================================================================
# ====================================== PRODUCTS ============================================

@login_required(login_url='joejee:user_signin')
def Admin_product(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(product_name__icontains = q)|Q(category__cat_name__icontains = q))
        Products = Product.objects.filter(multiple_q).order_by('id').reverse()
    else:
        Products = Product.objects.all().order_by('id').reverse()
    context = {
        'Products': Products,
    }
    return render(request,'products/products.html',context)

@login_required(login_url='joejee:user_signin')
def delete_product(request,id):
    if request.method == 'POST':
        pi = Product.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/products')
    

@login_required(login_url='joejee:user_signin')
def update_product(request,id):
    pi = Product.objects.get(pk=id)
    img_fm =ImagesFormSet(request.POST or None, request.FILES or None, instance= pi)
    if request.method == 'POST':
        fm = ProductForm(request.POST, request.FILES, instance=pi)
        if fm.is_valid() and img_fm.is_valid():
            fm.save()
            img_fm.save()
        return HttpResponseRedirect('/admin/products')
    else:
        fm = ProductForm( instance=pi)
    context = {
        'form':fm,
        'image_form':img_fm
    }
    return render(request, 'products/update_product.html',context)

ImagesFormSet = ProductImageFormSet = inlineformset_factory(Product,Images, form = ImagesForm,extra = 4)
@login_required(login_url='joejee:user_signin')
def add_product(request):
    if request.method == 'POST' :
        product_form = ProductForm(request.POST, request.FILES)
        images_form = ProductImageFormSet(request.POST,request.FILES, instance=Product())
        if product_form.is_valid() and images_form.is_valid():
            post = product_form.save(commit=False)
            post.save()
            images_form.instance = post
            images_form.save()
            return HttpResponseRedirect('/admin/products')
            form = ProductForm()
    else:
        product_form = ProductForm()
        images_form = ProductImageFormSet(instance=Product())
    context={
        'product_form':product_form,
        'image_form':images_form
    }
    return render(request, 'products/add_product.html',context)

# =================================================================================================
# =================================================================================================

# =============================================================================================
# ====================================== VARIATIONS ============================================
@login_required(login_url='joejee:user_signin')
def Admin_variation(request):
    vari = Variation.objects.all()
    context = {
        'variation': vari,
    }
    return render(request,'products/variation.html',context)

@login_required(login_url='joejee:user_signin')
def delete_variation(request,id):
    if request.method == 'POST':
        pi = Variation.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/variations')
    
@login_required(login_url='joejee:user_signin')
def update_variation(request,id):
    if request.method == 'POST':
        pi = Variation.objects.get(pk=id)
        fm = VariationForm(request.POST, instance=pi)
        if fm.is_valid:
            fm.save()
        return HttpResponseRedirect('/admin/variations')
    else:
        pi = Variation.objects.get(pk=id)
        fm = VariationForm( instance=pi)
    return render(request, 'products/update_variation.html',{'form':fm})

@login_required(login_url='joejee:user_signin')
def add_variation(request):
    if request.method == 'POST' :
        form = VariationForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect('/admin/variations')
            form = VariationForm()
    else:
        form = VariationForm()
    return render(request, 'products/add_variation.html',{'form':form})

# ====================================== VARIATIONS ============================================
#================================================================================================

# =============================================================================================
# ====================================== ORDERS ============================================
@login_required(login_url='joejee:user_signin')
def Admin_Orders(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(order_number__icontains = q)|Q(first_name__icontains = q)|Q(user__email__icontains = q)|Q(user__phone_number__icontains = q))
        orders = Order.objects.filter(multiple_q).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request,'products/orders_list.html',context)

@login_required(login_url='joejee:user_signin')
def admin_orders_details(request,order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal=0
    for i in order_detail:
        subtotal += i.product_price*i.quantity
    
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal,
    }
    return render(request,'products/admin_order_detail.html',context)

@login_required(login_url='joejee:user_signin')
def change_order_status(request):
    body = json.loads(request.body)
    try:
        order = Order.objects.get(order_number=body['order_number'])
        order.status=body['option']
        order.save()
    except Order.DoesNotExist:
        pass
    data = {
        'status':order.status,
        'message':"Not a Valid Coupon"
    }
    return JsonResponse(data)
        

@login_required(login_url='joejee:user_signin')
def admin_orders_confirm(request,order_id):
    order = Order.objects.get(order_number=order_id)
    order.status='Confirmed'
    order.save()
    return redirect('products:orders_list')

@login_required(login_url='joejee:user_signin')
def admin_orders_shipping(request,order_id):
    order = Order.objects.get(order_number=order_id)
    order.status='shipping'
    order.save()
    return redirect('products:orders_list')

@login_required(login_url='joejee:user_signin')
def admin_orders_delievered(request,order_id):
    order = Order.objects.get(order_number=order_id)
    order.status='Delivered'
    order.save()
    return redirect('products:orders_list')

# ==============================================================================
# ========================= COUPON =============================================
@login_required(login_url='joejee:user_signin')
def Admin_coupon(request):
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(code__icontains = q))
        coupons = Coupon.objects.filter(multiple_q)
    else:
        coupons = Coupon.objects.all()
    context = {
        'coupons': coupons,
    }
    return render(request,'products/coupon.html',context)

@login_required(login_url='joejee:user_signin')
def delete_coupon(request,id):
    if request.method == 'POST':
        pi = Coupon.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/coupon')
    

@login_required(login_url='joejee:user_signin')
def update_coupon(request,id):
    if request.method == 'POST':
        pi = Coupon.objects.get(pk=id)
        fm = CouponForm(request.POST, instance=pi)
        if fm.is_valid:
            fm.save()
        return HttpResponseRedirect('/admin/coupon')
    else:
        pi = Coupon.objects.get(pk=id)
        fm = CouponForm( instance=pi)
    return render(request, 'products/update_coupon.html',{'form':fm})

@login_required(login_url='joejee:user_signin')
def add_coupon(request):
    if request.method == 'POST' :
        form = CouponForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return HttpResponseRedirect('/admin/coupon')
            form = CouponForm()
    else:
        form = CouponForm()
    return render(request, 'products/add_coupon.html',{'form':form})
