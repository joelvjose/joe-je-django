from django.contrib.auth.forms import UserCreationForm
from .models import Account
from django import forms

class CustomUserForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'John'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'Doe'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'johndoe@abc.com'}))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control my-2', 'placeholder':'xxxxxxxxxx'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2', 'placeholder':'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control my-2', 'placeholder':'Confirm Password'}))
    
    class Meta:
        model = Account
        fields = ['first_name','last_name','email','phone_number','password1','password2']
        