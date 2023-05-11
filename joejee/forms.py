from django.contrib.auth.forms import UserCreationForm
from .models import Account,AddressBook
from django import forms

class CustomUserForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'John'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Doe'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'johndoe@abc.com'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'xxxxxxxxxx', 'pattern':'[789][0-9]{9}' }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2', 'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2', 'placeholder':'Confirm Password'}))
    
    class Meta:
        model = Account
        fields = ['first_name','last_name','email','phone_number','password1','password2']
        
class AddressBookForm(forms.ModelForm):
    # address =forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-1', 'placeholder':'Enter Address'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Last Name'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Phone Number'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'E-mail'}))
    address_line_1 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'House No & Locality'}))
    address_line_2 = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Address line 2(optional)'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'City'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'State'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Country'}))
    pincode = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Pincode'}))
    status = forms.BooleanField(required=False,widget=forms.CheckboxInput())
    
    class Meta:
        model = AddressBook
        # fields = ['first_name','last_name','phone','email','address_line_1','address_line_2','city','state','country','pincode','status']
        exclude = ("user",)