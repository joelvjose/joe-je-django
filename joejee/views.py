from django.forms import inlineformset_factory
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from products.models import Product,category,Images
from carts.models import CartItems
from carts.views import _cart_id
from .models import Account
from products import verify 

from .forms import CustomUserForm
from products.forms import VerifyForm,ImagesForm

from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q

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
        # images =ImagesFormSet(request.POST or None, request.FILES or None, instance= single_product)
        images = Images.objects.filter(product = single_product.id)
        in_cart = CartItems.objects.filter(cart__cart_id=_cart_id(request),product = single_product).exists() 
    except Exception as e:
        raise e
    
    context ={
        'single_product':single_product,
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