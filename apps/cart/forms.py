# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from ..lk.models import Profile
from .models import Cart


class CartCheckoutForm(forms.ModelForm):
    """
    Оформление корзины
    """
    email = forms.EmailField(label=_('E-mail'), required=False)

    class Meta:
        model = Cart
        fields = ('country', 'city', 'postal_code', 'address', 'phone', 'name', 'email')

    def __init__(self, *args, **kwargs):
        super(CartCheckoutForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = True
        self.fields['city'].required = True
        self.fields['postal_code'].required = False
        self.fields['address'].required = True
        self.fields['phone'].required = True
        self.fields['name'].required = True
        self.fields['email'].required = True

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if email:
    #         same_profile = Profile.objects.filter(email__iexact=email).first()
    #         if same_profile and self.instance.profile != same_profile:
    #             raise forms.ValidationError(_('Такой email уже занят.'))
    #     return email
