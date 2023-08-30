from typing import Any, Dict
from django import forms
from django.conf import settings

def action_validator(value):
    if not value in ['changePassword', 'removePassword', 'deleteUrl']:
        raise forms.ValidationError("Invalid Action")

class ShortLinkEditor(forms.Form):
    action = forms.CharField(max_length=15, required=True,validators=[action_validator])
    password = forms.CharField(max_length=settings.MAX_PASS_LENGTH,required=False, initial=None)
    password_protected = forms.BooleanField(required=False,initial=False)

    

class ShortLinkCreateForm(forms.Form):
    url = forms.URLField(max_length=settings.MAX_URL_LENGTH,required=True)
    password_protected = forms.BooleanField(required=False,initial=False)
    password = forms.CharField(max_length=settings.MAX_PASS_LENGTH,required=False, initial=None)

    def clean(self):
        cleaned_data = super().clean()
        password_protected = cleaned_data.get('password_protected')
        password = cleaned_data.get('password')

        if password_protected and not password:
            self.add_error('password', 'Please provide a password for password-protected URLs.')

        return cleaned_data

class ListShortLinkForm(forms.Form):
    skip = forms.IntegerField(required=False,initial=0)
    amount = forms.IntegerField(required=False, initial= settings.URLS_PER_PAGE)

    def clean(self) -> Dict[str, Any]:
        cleaned =  super().clean()
        
        if 'amount' not in cleaned or not cleaned['amount']:
            cleaned['amount'] = settings.URLS_PER_PAGE

        if 'skip'not in cleaned or not cleaned['skip']:
            cleaned['skip'] = 0
            
        return cleaned