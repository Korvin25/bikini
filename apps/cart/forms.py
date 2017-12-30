# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Cart


class CartCheckoutForm(forms.ModelForm):
    """
    Оформление корзины
    """

    class Meta:
        model = Cart
        fields = ('country', 'city', 'address', 'phone', 'name',)

    def __init__(self, *args, **kwargs):
        super(CartCheckoutForm, self).__init__(*args, **kwargs)
        self.fields['country'].required = True
        self.fields['city'].required = True
        self.fields['address'].required = True
        self.fields['phone'].required = True
        self.fields['name'].required = True
