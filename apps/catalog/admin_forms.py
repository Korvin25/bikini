# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from multiselectfield.forms.fields import MultiSelectFormField

from .models import AttributeOption, ExtraProduct, Product


class AttributeOptionInlineFormset(forms.BaseInlineFormSet):
    """
    Переопределяем формсет, чтобы передать значения в формы
    """

    def get_form_kwargs(self, index):
        kwargs = super(AttributeOptionInlineFormset, self).get_form_kwargs(index)
        kwargs['attribute'] = self.instance
        return kwargs


class AttributeOptionAdminForm(forms.ModelForm):
    video_id = 0

    class Meta:
        model = AttributeOption
        fields = '__all__'

    def __init__(self, attribute, *args, **kwargs):
        super(AttributeOptionAdminForm, self).__init__(*args, **kwargs)
        self.attribute = attribute

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        if not picture:
            if self.attribute.attr_type == 'color':
                color = self.cleaned_data.get('color')
                if not color:
                    raise forms.ValidationError('Загрузите картинку или выберите цвет.')
            else:
                raise forms.ValidationError('Обязательное поле.')
        return picture


class ChangeCategoryForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['category', ]

    def __init__(self, *args, **kwargs):
        super(ChangeCategoryForm, self).__init__(*args, **kwargs)
        self.fields['category'].required = True


class ChangeAttributesForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('id',)

    def __init__(self, *args, **kwargs):
        super(ChangeAttributesForm, self).__init__(*args, **kwargs)
        self.fields['attributes'] = MultiSelectFormField(label='Атрибуты',
                                                         choices=self.instance.category.attributes.values_list(
                                                            'id', 'admin_title'
                                                         ),
                                                         required=False,
                                                         min_choices=0)
        self.fields['attributes'].initial = list(self.instance.attributes.values_list('id', flat=True))
        self.fields['extra_products'] = MultiSelectFormField(label='Атрибуты',
                                                             choices=ExtraProduct.objects.all().values_list(
                                                                'id', 'admin_title'
                                                             ),
                                                             required=False,
                                                             min_choices=0)
        self.fields['extra_products'].initial = list(self.instance.extra_options.values_list('extra_product_id', flat=True))

    def save(self, commit=True):
        obj = super(ChangeAttributesForm, self).save(commit=False)
        attributes = self.cleaned_data.get('attributes')
        extra_products = self.cleaned_data.get('extra_products')
        obj.attributes = attributes
        obj.create_extra_products(extra_products)
        if commit:
            obj.save()
        return obj
