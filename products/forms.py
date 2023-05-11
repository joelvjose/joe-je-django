from django import forms
from .models import Product,category,Images,Variation,Coupon
from joejee.models import Account
from django.forms import DateInput

class AccountForm(forms.ModelForm):
    
    class Meta:
       model =  Account
       fields = ["first_name","last_name","email","phone_number","is_active","is_admin",]

class VerifyForm(forms.Form):
    # code = forms.CharField(max_length=8, required=True, help_text='Enter code')
    code = forms.CharField(max_length=8, required=True,widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Enter code'}))
    

       
class ProductForm(forms.ModelForm):
    
    class Meta:
       model =  Product
       fields = ["product_name","description","price","stock","image","is_available","category",]
       
class CategoryForm(forms.ModelForm):
    
    class Meta:
       model =  category
       fields = ["cat_name",]
       
class ImagesForm(forms.ModelForm):
    # images = forms.ImageField(widget=forms.FileInput(attrs={ "multiple": True}))
    class Meta:
        model = Images
        fields = ["images"]
        
class VariationForm(forms.ModelForm):
    
    class Meta:
       model =  Variation
       fields = ["product","variation_category","variation_value","price","stock","is_active"]
       
class CouponForm(forms.ModelForm):
    
    class Meta:
       model =  Coupon
       fields = ["code","discount","min_amount","active_date","expiry_date","active"]
       widgets = {
            'active_date': forms.SelectDateWidget(),
            'expiry_date': forms.SelectDateWidget(),
        }
