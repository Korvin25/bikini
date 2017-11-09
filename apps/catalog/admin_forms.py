# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import AttributeOption, Product


class AttributeOptionAdminForm(forms.ModelForm):
    video_id = 0

    class Meta:
        model = AttributeOption
        fields = '__all__'

    def _clean_required(self, key):
        value = self.cleaned_data.get(key)
        if not value:
            raise forms.ValidationError('Обязательное поле.')
        return value

    def clean_picture(self):
        return self._clean_required('picture')

    def clean_color(self):
        return self._clean_required('color')


class ChangeCategoryForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['category', ]

    def __init__(self, *args, **kwargs):
        super(ChangeCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = True
