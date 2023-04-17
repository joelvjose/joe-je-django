from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from products.models import Product,category,Images
from carts.models import CartItems,Cart
from carts.views import _cart_id
from .models import Account
from products import verify 

from .forms import CustomUserForm
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
    return render(request,'joejee/index.html')


    
def shop(request, category_slug=None):
    categories = None
    prod = None
    if 'q' in request.GET:
        q = request.GET['q']
        multiple_q = Q(Q(product_name__icontains = q)|Q(category__cat_name__icontains = q))
        prod = Product.objects.filter(multiple_q)
        paginator = Paginator(prod,9)
        page = request.GET.get('page')
        paged_prod = paginator.get_page(page)
        prod_count =prod.count()
    else:
        if category_slug is not None:
            categories = get_object_or_404(category,slug=category_slug)
            prod = Product.objects.filter(category= categories, is_available=True)
            paginator = Paginator(prod,9)
            page = request.GET.get('page')
            paged_prod = paginator.get_page(page)
            prod_count = prod.count()
        else:
            prod = Product.objects.all().filter(is_available = True).order_by('id')
            paginator = Paginator(prod,9)
            page = request.GET.get('page')
            paged_prod = paginator.get_page(page)
            prod_count =prod.count()
    
    context = {
        'products':paged_prod,
        'product_count':prod_count
    }
    return render(request,'joejee/shop.html',context)


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
            password1 = form.cleaned_data['password1']
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,phone_number=phone_number,email=email,password=password1)
            user.save()
            request.session['email']=email
            verify.send(phone_number)
            messages.success(request,"Registered Sucessfully! Verify OTP to Continue")
            return redirect('/verify/')
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
def dashboard(request):
    return render(request,'joejee/dashboard.html')

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
    