# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import update_wrapper

from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.filters import SimpleListFilter
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.safestring import mark_safe

from jet.admin import CompactInline
from modeltranslation.admin import TabbedTranslationAdmin, TranslationInlineModelAdmin
from salmonella.admin import SalmonellaMixin

from .admin_dynamic import (ProductOptionInlineFormset, ProductPhotoInlineFormset,
                            ProductOptionInlineForm, ProductPhotoInlineForm, ProductExtraOptionInlineForm,
                            ProductOptionAdmin, ProductPhotoAdmin, ProductExtraOptionAdmin,)
from .admin_forms import AttributeOptionInlineFormset, AttributeOptionAdminForm, ChangeCategoryForm, ChangeAttributesForm
from .models import (Attribute, AttributeOption, ExtraProduct, Category,
                     AdditionalProduct, Certificate,
                     Product, ProductOption, ProductExtraOption, ProductPhoto,)
from .translation import *


def _pop(_list, name):
    if name in _list:
        _list.pop(_list.index(name))
    return _list


# === Атрибуты (справочники) ===

class AttributeOptionInline(TranslationInlineModelAdmin, CompactInline):
    model = AttributeOption
    form = AttributeOptionAdminForm
    formset = AttributeOptionInlineFormset
    fields = ('title', 'color', 'picture', 'order',)
    min_num = 1
    extra = 0

    def get_fieldsets(self, request, obj=None):
        """
        Выводим необязательные поля (picture и color) в зависимости от типа атрибута
        """
        fieldsets = list(super(AttributeOptionInline, self).get_fieldsets(request, obj))
        fields = fieldsets[0][1]['fields']
        if obj.attr_type == 'color':
            # _pop(fields, 'picture')
            pass
        elif obj.attr_type == 'size':
            _pop(fields, 'picture')
            _pop(fields, 'color')
        elif obj.attr_type == 'style':
            _pop(fields, 'color')
        elif obj.attr_type == 'text':
            _pop(fields, 'picture')
            _pop(fields, 'color')
        return fieldsets


@admin.register(Attribute)
class AttributeAdmin(TabbedTranslationAdmin):
    list_display = ('admin_title', 'title_ru', 'category', 'attr_type', 'slug', 'display_type', 'neighbor', 'order',)
    list_editable = ('order',)
    list_filter = ('attr_type', 'category', 'display_type',)
    ordering = ['-category', 'attr_type', 'order', 'id', ]
    fieldsets = (
        (None, {
            'fields': ('admin_title', 'title', 'slug', 'category', 'attr_type', 'neighbor',
                       # 'position', 'add_to_price',
                       'display_type', 'order',),
        }),
        ('Варианты', {
            'fields': ('options_instruction',),
        }),
    )
    readonly_fields = ('options_instruction',)
    inlines = [AttributeOptionInline, ]

    def get_fieldsets(self, request, obj=None):
        """
        Если объект уже создан, вместо таба с инструкцией по вариантам будет таб с инлайнами
        """
        fieldsets = list(super(AttributeAdmin, self).get_fieldsets(request, obj))
        if obj:
            del fieldsets[1]
        return fieldsets

    def get_inline_instances(self, request, obj=None):
        """
        Если объект уже создан (а главное, выбран тип атрибута), показываем инлайны
        """
        if not obj:
            return []
        return super(AttributeAdmin, self).get_inline_instances(request, obj)

    def get_readonly_fields(self, request, obj=None):
        """
        Если объект уже создан и добавлены товары - не даем менять slug (чтобы не поломалось поле attrs)
        (+ не даем метять тип атрибута, чтобы не поломались инлайны у вариантов)
        """
        readonly_fields = list(super(AttributeAdmin, self).get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append('attr_type')
            readonly_fields.append('category')
            # q = {'attrs__{}__gt'.format(obj.slug): []}
            # if Product.objects.filter(**q).count():
            #     readonly_fields.append('slug')
            readonly_fields.append('slug')
            # if obj.category != 'extra':
            #     readonly_fields.append('add_to_price')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        """
        Реализуем аналог symmetrical=True у OneToOneField
        """
        old_neighbor = (Attribute.objects.get(id=obj.id).neighbor if obj.id
                        else None)
        s = super(AttributeAdmin, self).save_model(request, obj, form, change)
        neighbor = obj.neighbor

        if neighbor != old_neighbor:
            if old_neighbor:
                old_neighbor.set_neighbor(None)
            if neighbor:
                neighbor.set_neighbor(obj)
        return s


@admin.register(ExtraProduct)
class ExtraProductAdmin(TabbedTranslationAdmin):
    list_display = ('admin_title', 'title_ru', 'slug', 'order', 'show_attributes',)
    list_editable = ('order',)
    fieldsets = (
        (None, {
            'fields': ('admin_title', 'title', 'slug', 'order', 'attributes',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super(ExtraProductAdmin, self).get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append('slug')
        return readonly_fields


# === Категории ===

@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('show_sex', 'title_ru', 'order', 'show_attributes',)
    list_display_links = ('title_ru',)
    list_editable = ('order',)
    list_filter = ('sex',)
    list_per_page = 200
    fieldsets = (
        (None, {
            'fields': ('sex', 'title', 'order', 'attributes',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    search_fields = ['title', ]


# === Дополнительные товары + сертификаты ===

# @admin.register(AdditionalProduct)
# class AdditionalProductAdmin(TabbedTranslationAdmin):
#     list_display = ('id', 'title', 'show', 'price_rub', 'price_eur', 'price_usd',)
#     list_display_links = ('id', 'title',)
#     list_filter = ('show',)
#     list_per_page = 200
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'vendor_code', 'photo',
#                        ('price_rub', 'price_eur', 'price_usd',), 'show',),
#         }),
#     )
#     search_fields = ['title', 'vendor_code', ]


@admin.register(Certificate)
class CertificateProductAdmin(TabbedTranslationAdmin):
    list_display = ('id', 'title', 'show', 'price_rub', 'price_eur', 'price_usd',)
    list_display_links = ('id', 'title',)
    list_filter = ('show',)
    list_per_page = 200
    fieldsets = (
        (None, {
            'fields': ('title', 'vendor_code',
                       ('price_rub', 'price_eur', 'price_usd',), 'show',),
        }),
    )
    search_fields = ['title', 'vendor_code', ]


# === Товары ===

class HasAttrsFilter(SimpleListFilter):
    title = 'Есть атрибуты?'
    parameter_name = 'has_attrs'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        return (queryset.filter(attrs={}) if self.value() == 'no'
                else queryset.exclude(attrs={}) if self.value() == 'yes'
                else queryset)


class ProductOptionInline(ProductOptionAdmin):
    model = ProductOption
    form = ProductOptionInlineForm
    formset = ProductOptionInlineFormset
    fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock')
    min_num = 1
    extra = 0


class ProductExtraOptionInline(ProductExtraOptionAdmin):
    model = ProductExtraOption
    form = ProductExtraOptionInlineForm
    fields = ('title', 'extra_product', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)
    readonly_fields = ('extra_product',)

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None


class ProductPhotoInline(ProductPhotoAdmin):
    model = ProductPhoto
    form = ProductPhotoInlineForm
    formset = ProductPhotoInlineFormset
    fields = ('photo',)

    def get_extra(self, request, obj=None):
        extra = (0 if obj and obj.photos.count()
                 else 1)
        return extra


@admin.register(Product)
class ProductAdmin(SalmonellaMixin, TabbedTranslationAdmin):
    change_category_template = 'admin/catalog/product/change_category.html'
    change_attributes_template = 'admin/catalog/product/change_attributes.html'

    def change_category_view(self, request, id, form_url='', extra_context=None):
        opts = Product._meta
        try:
            obj = Product.objects.get(pk=id)
        except (Product.DoesNotExist, ValueError) as e:
            raise Http404
        form = ChangeCategoryForm(request.POST, instance=obj) if request.POST else ChangeCategoryForm(instance=obj)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj:
            old_category = obj.category

        if form.is_valid():
            new_category = form.cleaned_data['category']
            form.save()

            if new_category != old_category:
                obj.set_attributes_from_category(new_category)

            category = obj.category
            self.message_user(request,
                              mark_safe('''Категория у товара "<a href="/admin/catalog/product/{}/change/">{}</a>"
                                 изменена на "<a href="/admin/catalog/category/{}/change/">{}</a>".'''.format(
                                    id, obj.__unicode__(), category.id, category.__unicode__(),
                                )),
                              messages.SUCCESS)
            return HttpResponseRedirect('/admin/catalog/product/{}/change_attributes/'.format(id))

        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)

        context = {
            'title': 'Изменить категорию у товара %s' % obj,
            'has_change_permission': self.has_change_permission(request, obj),
            'form_url': form_url,
            'form': form,
            'opts': opts,
            'errors': form.errors,
            'app_label': opts.app_label,
            'original': obj,
        }
        context.update(extra_context or {})
        return render(request, self.change_category_template, context)

    def change_attributes_view(self, request, id, form_url='', extra_context=None):
        opts = Product._meta
        try:
            obj = Product.objects.get(pk=id)
        except (Product.DoesNotExist, ValueError) as e:
            raise Http404
        form = ChangeAttributesForm(request.POST, instance=obj) if request.POST else ChangeAttributesForm(instance=obj)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if form.is_valid():
            form.save()
            self.message_user(request,
                              mark_safe('''Атрибуты у товара "<a href="/admin/catalog/product/{}/change/">{}</a>"
                                           изменены.'''.format(id, obj.__unicode__())),
                              messages.SUCCESS)
            return HttpResponseRedirect('/admin/catalog/product/{}/change/'.format(id))

        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)

        context = {
            'title': 'Изменить атрибуты у товара %s' % obj,
            'has_change_permission': self.has_change_permission(request, obj),
            'form_url': form_url,
            'form': form,
            'opts': opts,
            'errors': form.errors,
            'app_label': opts.app_label,
            'original': obj,
        }
        context.update(extra_context or {})
        return render(request, self.change_attributes_template, context)

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name
        urls = [
            url(r'^(.+)/change_category/$',
                wrap(self.change_category_view),
                name='%s_%s_change_category' % info),
            url(r'^(.+)/change_attributes/$',
                wrap(self.change_attributes_view),
                name='%s_%s_change_attributes' % info),
        ]
        super_urls = super(ProductAdmin, self).get_urls()
        return urls + super_urls

    list_display = ('id', 'title', 'category', 'show', 'has_attrs', 'show_at_homepage',
                    'order_at_homepage', 'add_dt', 'in_stock', 'vendor_code')
    list_display_links = ('id', 'title',)
    list_editable = ('order_at_homepage', 'in_stock', 'vendor_code')
    list_filter = ('show', HasAttrsFilter, 'show_at_homepage', 'add_dt', 'category',)
    list_per_page = 200
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'category', 'vendor_code', 'photo',
                       ('price_rub', 'price_eur', 'price_usd',), 'text', 'in_stock',),
        }),
        ('Настройки показа на сайте', {
            'fields': ('show', 'show_at_homepage', 'order_at_homepage', 'add_dt',),
        }),
        ('Сопутствующие товары', {
            # 'fields': ('additional_products', 'associated_products', 'also_products',),
            'fields': ('associated_products', 'also_products',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
        ('Варианты товара', {
            'fields': ('options_instruction',),
        }),
        ('Фото', {
            'fields': ('photos_instruction',),
        }),
        ('Дополнительные товары', {
            'fields': ('extra_options_instruction',),
        }),
    )
    readonly_fields = ('id', 'add_dt', 'options_instruction', 'extra_options_instruction', 'photos_instruction',
                       'show_category', 'show_attributes',)
    inlines = [ProductOptionInline, ProductPhotoInline, ProductExtraOptionInline, ]
    # # raw_id_fields = ('additional_products', 'associated_products', 'also_products',)
    # salmonella_fields = ('additional_products', 'associated_products', 'also_products',)
    salmonella_fields = ('associated_products', 'also_products',)
    search_fields = ['title', 'vendor_code', 'subtitle', 'text', ]

    def get_fieldsets(self, request, obj=None):
        """
        Если объект уже создан, вместо таба с инструкциями будут табы с инлайнами.
        Также вместо поля выбора категории показываем ридонли-поле с ссылкой на страниу выбора
        """
        fieldsets = list(super(ProductAdmin, self).get_fieldsets(request, obj))
        if obj:
            # fieldsets[0][1]['fields'][2] = 'show_category'
            fieldsets[0][1]['fields'][12] = 'show_category'
            del fieldsets[4]
            del fieldsets[4]
            if obj.extra_options.count():
                del fieldsets[4]
        return fieldsets

    def get_inline_instances(self, request, obj=None):
        """
        Если объект уже создан (а главное, выбрана категория), показываем инлайны
        """
        if not obj:
            return []
        s = super(ProductAdmin, self).get_inline_instances(request, obj)
        if not obj.extra_options.count():
            s = s[:2]
        return s

    def get_readonly_fields(self, request, obj=None):
        """
        Если объект уже создан, не даем менять категорию (только на отдельной странице)
        """
        readonly_fields = list(super(ProductAdmin, self).get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append('category')
        return readonly_fields

    def save_formset(self, request, form, formset, change):
        """
        Обновляем поле attrs у товара после сохранения всех его вариантов
        """
        s = super(ProductAdmin, self).save_formset(request, form, formset, change)
        if formset.model == ProductOption:
            formset.instance.set_attrs()
        return s
