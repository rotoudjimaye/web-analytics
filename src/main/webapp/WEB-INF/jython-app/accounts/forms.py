__author__ = 'rotoudjimaye'

import django.forms as forms
from django.contrib import auth
from webanalytics.models import Account

class AccountLoginForm(forms.Form):
    """ A form used for logging in purposes """
    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    def clean(self):
        cleaned_data = super(AccountLoginForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if super(AccountLoginForm, self).is_valid():
            try:
                user = auth.authenticate(username=username,password=password)
                if not user.is_active: raise Exception("User account not active")
                account = Account.objects.get(user=user)
                cleaned_data['user'] = user
                cleaned_data['account'] = account
            except Exception, e:
                raise forms.ValidationError("Your username and password combination is not valid")
        return cleaned_data
