# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import CallbackOrder


class CallbackOrderForm(forms.ModelForm):
    """
    Заказ обратного звонка
    """

    class Meta:
        model = CallbackOrder
        fields = ('name', 'phone',)
