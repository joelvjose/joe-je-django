from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from joejee.models import Account
from .models import category,Product,Images,Variation
from .forms import AccountForm,ProductForm,CategoryForm,ImagesForm,VariationForm

# Create your views here.
from django.shortcuts import render

def Admin_home(request):
    return render(request,'products/index.html')

# ============================================================================================
# ====================================== CUSTOMER PANEL ======================================
def Admin_customer(request):
    users = Account.objects.filter(is_superadmin=False)
    context = {
        'users': users,
    }
    return render(request,'products/customer.html',context)

# -====================== customer add,edit and update data===========================
def unblock_customer(request,id):
    if request.method == 'POST':
        pi = Account.objects.get(pk=id)
        pi.is_active=True
        pi.save()
        return HttpResponseRedirect('/admin/customer')
    

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
def Admin_category(request):
    cat = category.objects.all()
    context = {
        'category': cat,
    }
    return render(request,'products/category.html',context)

def delete_category(request,id):
    if request.method == 'POST':
        pi = category.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/Category')
    

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

def Admin_product(request):
    Products = Product.objects.all()
    context = {
        'Products': Products,
    }
    return render(request,'products/products.html',context)

def delete_product(request,id):
    if request.method == 'POST':
        pi = Product.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/products')
    

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
def Admin_variation(request):
    vari = Variation.objects.all()
    context = {
        'variation': vari,
    }
    return render(request,'products/variation.html',context)

def delete_variation(request,id):
    if request.method == 'POST':
        pi = Variation.objects.get(pk=id)
        pi.delete()
        return HttpResponseRedirect('/admin/variations')
    

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
# =============================================================================================

