# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

# from jet.admin import CompactInline
from multiselectfield.forms.fields import MultiSelectFormField

from .models import ExtraProduct, ProductOption, ProductExtraOption, ProductPhoto, Category


"""
Варианты товаров и фото
"""

# ---- формсеты ----

class ProductOptionInlineFormset(forms.BaseInlineFormSet):

    def get_form_kwargs(self, index):
        # передаем значения в формы
        kwargs = super(ProductOptionInlineFormset, self).get_form_kwargs(index)
        kwargs['attrs_list'] = self.instance.get_attrs_list()
        return kwargs


class ProductPhotoInlineFormset(forms.BaseInlineFormSet):

    def get_form_kwargs(self, index):
        # передаем значения в формы
        kwargs = super(ProductPhotoInlineFormset, self).get_form_kwargs(index)
        kwargs['attrs_list'] = self.instance.get_attrs_list(filter='photos')
        return kwargs


# ---- формы ----

class AttrsBasedInlineFormMixin(object):
    attrs_min_choices = 1

    def __init__(self, attrs_list, *args, **kwargs):
        """
        Создаем динамические поля на основе product.attrs
        """
        super(AttrsBasedInlineFormMixin, self).__init__(*args, **kwargs)

        for field in self.fields.keys():
            # избавляемся от динамических полей, оставшихся от других моделей
            if field not in self.Meta.default_fields:
                del self.fields[field]

        self.attrs_list = attrs_list
        for attr in self.attrs_list:
            self.fields[attr['slug']] = MultiSelectFormField(label=attr['title'], choices=attr['choices'],
                                                             required=(self.attrs_min_choices>0),
                                                             min_choices=self.attrs_min_choices)
            self.fields[attr['slug']].widget.attrs = {'class': 'can_be_collapsed'}
            if self.instance:
                self.fields[attr['slug']].initial = self.instance.attrs.get(attr['slug'], list())

    def save(self, commit=True):
        """
        Сохраняем данные из динамических полей в поле attrs у объекта
        """
        obj = super(AttrsBasedInlineFormMixin, self).save(commit=False)
        obj.attrs = {}
        for attr in self.attrs_list:
            obj.attrs[attr['slug']] = [int(c) for c in self.cleaned_data.get(attr['slug'])]
        if commit:
            obj.save()
        return obj


class ProductOptionInlineForm(AttrsBasedInlineFormMixin, forms.ModelForm):
    attrs_min_choices = 1

    class Meta:
        model = ProductOption
        fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)
        default_fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)


class ProductPhotoInlineForm(AttrsBasedInlineFormMixin, forms.ModelForm):
    attrs_min_choices = 0

    class Meta:
        model = ProductPhoto
        # fields = ('title', 'photo', 'photo_f',)
        # default_fields = ('title', 'photo', 'photo_f',)
        fields = ('title', 'photo_f',)
        default_fields = ('title', 'photo_f',)


class ProductExtraOptionInlineForm(forms.ModelForm):
    attrs_min_choices = 1

    class Meta:
        model = ProductExtraOption
        fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)
        default_fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)

    def __init__(self, *args, **kwargs):
        super(ProductExtraOptionInlineForm, self).__init__(*args, **kwargs)

        # for field in self.fields.keys():
        #     # избавляемся от динамических полей, оставшихся от других доп.товаров
        #     if field not in self.Meta.default_fields:
        #         del self.fields[field]

        if self.instance and self.instance.extra_product_id:
            self.attrs_list = self.instance.extra_product.get_attrs_list()
            for attr in self.attrs_list:
                self.fields[attr['slug']] = MultiSelectFormField(label=attr['title'], choices=attr['choices'],
                                                                 required=(self.attrs_min_choices>0),
                                                                 min_choices=self.attrs_min_choices)
                self.fields[attr['slug']].initial = self.instance.attrs.get(attr['slug'], list())
                self.fields[attr['slug']].widget.attrs = {'class': 'can_be_collapsed'}
                
        else:
            self.attrs_list = []

        attrs_slugs = [attr['slug'] for attr in self.attrs_list]

        for slug, field in self.fields.items():
            if isinstance(field, MultiSelectFormField):
                if slug not in attrs_slugs:
                    field.widget.attrs = {'class': 'hide_me'}

    def save(self, commit=True):
        """
        Сохраняем данные из динамических полей в поле attrs у объекта
        """
        obj = super(ProductExtraOptionInlineForm, self).save(commit=False)
        obj.attrs = {}
        for attr in self.attrs_list:
            obj.attrs[attr['slug']] = [int(c) for c in self.cleaned_data.get(attr['slug'])]
        if commit:
            obj.save()
        return obj


# ---- admin ----

class AttrsBasedAdminMixin(object):
    attrs_min_choices = 1

    def get_attrs_list(self, obj):
        return obj.get_attrs_list()

    def get_fields(self, request, obj=None):
        """
        from stackoverflow
        """
        fields = list(super(AttrsBasedAdminMixin, self).get_fields(request, obj))
        new_fields = []

        if obj:
            attrs_list = self.get_attrs_list(obj)
            for attr in attrs_list:
                new_fields.append((attr['slug'], MultiSelectFormField(label=attr['title'], choices=attr['choices'],
                                                                      required=(self.attrs_min_choices>0),
                                                                      min_choices=self.attrs_min_choices)))
            for f in new_fields:
                fields = fields + [f[0]]
                self.form.declared_fields.update({f[0]:f[1]})
            return fields

    def get_new_fields_names(self, obj):
        return obj.get_attrs_slugs()

    def get_fieldsets(self, request, obj=None):
        """
        from stackoverflow
        """
        fieldsets = super(AttrsBasedAdminMixin, self).get_fieldsets(request, obj)
        if obj:
            fields = list(fieldsets[0][1]['fields'])
            new_field_names = self.get_new_fields_names(obj)
            fields += new_field_names
        return fieldsets


class ProductOptionAdmin(AttrsBasedAdminMixin, admin.StackedInline):  # CompactInline
    pass


class ProductPhotoAdmin(AttrsBasedAdminMixin, admin.StackedInline):  # CompactInline
    attrs_min_choices = 0

    def get_attrs_list(self, obj):
        return obj.get_attrs_list(filter='photos')

    def get_new_fields_names(self, obj):
        return obj.get_attrs_slugs(filter='photos')


class ProductExtraOptionAdmin(AttrsBasedAdminMixin, admin.StackedInline):  # CompactInline
    attrs_min_choices = 0

    def get_attrs_list(self, obj):
        return ExtraProduct.get_all_attrs_list()

    def get_new_fields_names(self, obj):
        return ExtraProduct.get_all_attrs_slugs()
