# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from multiselectfield.forms.fields import MultiSelectFormField

from .models import ProductOption, ProductPhoto, Category


class AttrsInlineFormset(forms.BaseInlineFormSet):
    """
    Переопределяем формсет, чтобы передать значения в формы
    """

    def get_form_kwargs(self, index):
        kwargs = super(AttrsInlineFormset, self).get_form_kwargs(index)
        kwargs['attrs_list'] = self.instance.category.attrs_list
        return kwargs


class AttrsInlineFormMixin(object):
    attrs_min_choices = 1

    def __init__(self, attrs_list, *args, **kwargs):
        """
        Создаем динамические поля на основе product.category.attrs
        """
        super(AttrsInlineFormMixin, self).__init__(*args, **kwargs)

        self.attrs_list = attrs_list
        for attr in self.attrs_list:
            self.fields[attr['slug']] = MultiSelectFormField(label=attr['title'], choices=attr['choices'],
                                                             required=(self.attrs_min_choices>0),
                                                             min_choices=self.attrs_min_choices)
            if self.instance:
                self.fields[attr['slug']].initial = self.instance.attrs.get(attr['slug'])

    def save(self, commit=True):
        """
        Сохраняем данные с динамических полей в поле attrs у объекта
        """
        obj = super(AttrsInlineFormMixin, self).save(commit=False)
        obj.attrs = {}
        for attr in self.attrs_list:
            obj.attrs[attr['slug']] = [int(c) for c in self.cleaned_data.get(attr['slug'])]
        if commit:
            obj.save()
        return obj


class ProductOptionInlineForm(AttrsInlineFormMixin, forms.ModelForm):
    attrs_min_choices = 1

    class Meta:
        model = ProductOption
        fields = '__all__'


class ProductPhotoInlineForm(AttrsInlineFormMixin, forms.ModelForm):
    attrs_min_choices = 0

    class Meta:
        model = ProductPhoto
        fields = '__all__'


class AttrsAdminMixin(object):
    attrs_min_choices = 1

    def get_fields(self, request, obj=None):
        """
        from stackoverflow
        """
        fields = list(super(AttrsAdminMixin, self).get_fields(request, obj))
        new_fields = []

        if obj and obj.category_id:
            attrs_list = obj.category.attrs_list
            for attr in attrs_list:
                new_fields.append((attr['slug'], MultiSelectFormField(label=attr['title'], choices=attr['choices'],
                                                                      required=(self.attrs_min_choices>0),
                                                                      min_choices=self.attrs_min_choices)))
            for f in new_fields:
                fields = fields + [f[0]]
                self.form.declared_fields.update({f[0]:f[1]})
            return fields

    def get_fieldsets(self, request, obj=None):
        """
        from stackoverflow
        """
        fieldsets = super(AttrsAdminMixin, self).get_fieldsets(request, obj)
        if obj and obj.category_id:
            fields = list(fieldsets[0][1]['fields'])
            new_field_names = obj.category.attrs_slugs
            fields += new_field_names
        return fieldsets
