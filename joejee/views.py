from django.forms import inlineformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from products.models import Product,category,Images
from carts.models import CartItems,Cart
from carts.views import _cart_id
from .models import Account,AddressBook
from products import verify
from orders.models import Order,OrderProduct

from .forms import CustomUserForm,AddressBookForm
from products.forms import VerifyForm,ImagesForm

from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.views import _cart_id

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        if request.user.is_superadmin:
            return redirect('products:Admin_Home')
    products=Product.objects.all().order_by('-id')[:8]
    first_product=Product.objects.latest('id')
    context ={
        'products':products,
        'first_product':first_product,
    }
    return render(request,'joejee/index.html',context)

def contact(request):
    return render(request,'joejee/contact.html')

    
def shop(request, category_slug=None):
    categories = None
    prod = None
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(product_name__icontains = q)|Q(category__cat_name__icontains = q))
        prod = Product.objects.filter(multiple_q).order_by('-id')
        paginator = Paginator(prod,9)
        page = request.GET.get('page')
        paged_prod = paginator.get_page(page)
        prod_count =prod.count()
    elif 'p' in request.GET:
        p = int(request.GET['p'])
        # multiple_q = Q(Q(product_name__icontains = q)|Q(category__cat_name__icontains = q))
        prod = Product.objects.filter(price__range=(0, p)).order_by('-id')
        paginator = Paginator(prod,9)
        page = request.GET.get('page')
        paged_prod = paginator.get_page(page)
        prod_count =prod.count()
    else:
        if category_slug is not None:
            categories = get_object_or_404(category,slug=category_slug)
            prod = Product.objects.filter(category= categories, is_available=True).order_by('-id')
            paginator = Paginator(prod,9)
            page = request.GET.get('page')
            paged_prod = paginator.get_page(page)
            prod_count = prod.count()
        else:
            prod = Product.objects.all().filter(is_available = True).order_by('-id')
            paginator = Paginator(prod,9)
            page = request.GET.get('page')
            paged_prod = paginator.get_page(page)
            prod_count =prod.count()
    
    context = {
        'products':paged_prod,
        'product_count':prod_count
    }
    return render(request,'joejee/shop.html',context)

def search_products(request):
    # a_id = request.GET['id']
    # AddressBook.objects.update(status= False)
    # AddressBook.objects.filter(id=a_id).update(status=True)
    products= Product.objects.all()
    product_list=[]
    for product in products:
        product_list.append(product.product_name)
   
    return JsonResponse({'product_names':product_list})

# ImagesFormSet = ProductImageFormSet = inlineformset_factory(Product,Images, form = ImagesForm,extra = 4)
def product_detail(request,category_slug=None,product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        original_price = int(single_product.price*1.2)
        # images =ImagesFormSet(request.POST or None, request.FILES or None, instance= single_product)
        images = Images.objects.filter(product = single_product.id)
        in_cart = CartItems.objects.filter(cart__cart_id=_cart_id(request),product = single_product).exists() 
    except Exception as e:
        raise e
    
    context ={
        'single_product':single_product,
        'original_price': original_price,
        'images':images,
        'in_cart':in_cart
    }
    
    return render(request,'joejee/shop-details.html',context)

# ============================ AUTHENTICATION ===============================

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id= _cart_id(request))
                is_cart_item_exist = CartItems.objects.filter(cart = cart).exists()
                if is_cart_item_exist:
                    cart_item = CartItems.objects.filter(cart=cart)
                    product_variation =[]
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                        
                    cart_item = CartItems.objects.filter(user= user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pv in product_variation:
                        if pv in ex_var_list:
                            index = ex_var_list.index(pv)
                            item_id = id[index]
                            item = CartItems.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItems.objects.filter(cart= cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                
            except:
                pass
            auth.login(request,user)
            messages.success(request,'You have been sucessfully logged in.!')
            return redirect('/')
        else:
            messages.error(request,'Invalid user credentials!')
            return redirect('/signin/')
    return render(request,'products/signin.html')

def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email'] 
            phone_number = form.cleaned_data['phone_number']
            phone_number='+91' + phone_number
            password1 = form.cleaned_data['password1']
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,phone_number=phone_number,email=email,password=password1)
            user.save()
            request.session['email']=email
            try:
                verify.send(phone_number)
                messages.success(request,"Registered Sucessfully! Verify OTP to Continue")
                return redirect('/verify/')
            except:
                messages.error(request,"Invalid Mobile number")
            
    context = {'form':form}
    return render(request,'products/signup.html',context)

def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            user = Account._default_manager.get(email=request.session.get('email'))
            if verify.check(user.phone_number, code):
                user.is_active = True
                user.is_verified = True
                user.save()
                return redirect('/signin/')
    else:
        form = VerifyForm()
    return render(request, 'products/verify.html', {'form': form})

def logout(request):
    auth.logout(request)
    return redirect('/')

# =============================// DASHBOARD \\=============================
@login_required(login_url='joejee:user_signin')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered = True)
    order_count = orders.count()
    context ={
        'order_count':order_count,
    }
    return render(request,'joejee/dashboard.html',context)

@login_required(login_url='joejee:user_signin')
def my_orders(request):
    orders = Order.objects.filter(user= request.user, is_ordered= True).order_by('-created_at')
    context ={
        'orders':orders
    }
    return render(request,'joejee/my_orders.html',context)

def cancel_order(request,order_id):
    order = Order.objects.get(order_number=order_id)
    order.status='Cancelled'
    order.save()
    return redirect('joejee:my_orders')
    

@login_required(login_url='joejee:user_signin')
def orders_details(request,order_id):
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
    return render(request,'joejee/order_detail.html',context)


@login_required(login_url='joejee:user_signin')
def change_password(request):
    if request.method=="POST":
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']
        
        user = Account.objects.get(email__exact=request.user.email)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                return redirect('/')
                messages.success(request,'Password updated.!')
            else:
                messages.success(request,'Enter correct password.!')
                return redirect('joejee:change_password')
        else:
            messages.success(request,'Passwords doesnot match.!')
            return redirect('joejee:change_password')
    return render(request,'joejee/change_password.html')

 
@login_required(login_url='joejee:user_signin')   
def my_addresses(request):
    addresses = AddressBook.objects.filter(user= request.user).order_by('-id')
    context = {
        'addresses':addresses
    }
    return render(request, 'joejee/my_addresses.html',context)
    
    
def save_address(request):
    form = AddressBookForm()
    if request.method == "POST":
        form = AddressBookForm(request.POST)
        if form.is_valid():
            saveform=form.save(commit=False)
            saveform.user= request.user
            saveform.save()
            messages.success(request,"New Address added sucessfully.!")
            return redirect('joejee:my_addresses')
    context={
        'form':form
    }
    return render(request, 'joejee/add-address.html',context)
    
def activate_address(request):
    a_id = request.GET['id']
    AddressBook.objects.update(status= False)
    AddressBook.objects.filter(id=a_id).update(status=True)
    context = {
        'bool': True
    }
    return JsonResponse({'bool':True})
    
# ===========================================================================
def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site =get_current_site(request)
            mail_subject = 'Joe&Jee : Reset your password'
            message = render_to_string( 'joejee/reset_account_password.html', {
                'user': user,
                'domain' : current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token' : default_token_generator.make_token(user),
                })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('/signin/')
        else:
            messages.error(request, 'Account does not exists.! Please Sign in to continue..!')
            return redirect('/signup/')
    return render(request,'products/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError,OverflowError, Account.DoesNotExist):
        user = None
    
    if user  is not None and default_token_generator.check_token(user, token):
        request.session['uid']= uid
        messages.success(request,'Please reset your password.!')
        return redirect('joejee:resetpassword')
    else:
        messages.error(request, 'Sorry, the activation link has expired.!')
        return redirect('/signin/')
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password updated sucessfully..!')
            return redirect('/signin/')
        else:
            messages.error(request, 'Password does not match..!')
            return redirect('joejee:resetpassword')
    else:
        return render(request, 'products/reset-password.html' )
    