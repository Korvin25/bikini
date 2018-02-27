# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import MenuItem


class MenuItemAdminForm(forms.ModelForm):

    class Meta:
        model = MenuItem
        fields = '__all__'

    def clean_link(self):
        page = self.cleaned_data.get('page')
        link = self.cleaned_data.get('link')

        if not (page or link):
            raise forms.ValidationError('Укажите или страницу, или ссылку.')

        return link
