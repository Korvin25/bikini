# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import MenuItem


class MenuItemAdminForm(forms.ModelForm):

    class Meta:
        model = MenuItem
        fields = '__all__'

    def clean_link_ru(self):
        page = self.cleaned_data.get('page')
        link_ru = self.cleaned_data.get('link_ru')

        if not (page or link_ru):
            raise forms.ValidationError('Укажите или страницу (выше), или ссылку.')

        return link_ru
