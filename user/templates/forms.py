from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30, min_length=4)