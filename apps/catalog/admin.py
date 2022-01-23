# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import update_wrapper

from django.contrib import admin, messages
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.filters import SimpleListFilter
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, render_to_response
from django.template.context_processors import csrf
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin
# from jet.admin import CompactInline
from modeltranslation.admin import TabbedTranslationAdmin, TranslationInlineModelAdmin, TranslationStackedInline
from pytils.numeral import choose_plural
from salmonella.admin import SalmonellaMixin
from suit import apps

# from ..content.models import Video
from .admin_dynamic import (ProductOptionInlineFormset, ProductPhotoInlineFormset,
                            ProductOptionInlineForm, ProductPhotoInlineForm, ProductExtraOptionInlineForm,
                            ProductOptionAdmin, ProductPhotoAdmin, ProductExtraOptionAdmin,)
from .admin_forms import (UpdateProductsDataForm,
                          AttributeOptionInlineFormset, AttributeOptionAdminForm,
                          ProductAdminForm, ChangeCategoriesForm, ChangeAttributesForm,
                          SpecialOfferAdminForm,)
from .models import (Attribute, AttributeOption, ExtraProduct, Category,
                     # AdditionalProduct,
                     Certificate, GiftWrapping,
                     Product, ProductOption, ProductExtraOption, ProductPhoto,
                     ProductTab, ProductTabSection,
                     SpecialOfferCategory, SpecialOffer,)
from .translation import *  # noqa


def _pop(_list, name):
    if name in _list:
        _list.pop(_list.index(name))
    return _list


# === Атрибуты (справочники) ===

class AttributeOptionInline(TranslationInlineModelAdmin, admin.StackedInline):  # CompactInline
    model = AttributeOption
    form = AttributeOptionAdminForm
    formset = AttributeOptionInlineFormset
    fields = ('title', 'color', 'picture', 'admin_show_picture', 'order',)
    readonly_fields = ('admin_show_picture',)
    suit_classes = 'suit-tab suit-tab-options'
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
            _pop(fields, 'admin_show_picture')
            _pop(fields, 'color')
        elif obj.attr_type == 'style':
            _pop(fields, 'color')
        elif obj.attr_type == 'text':
            _pop(fields, 'picture')
            _pop(fields, 'admin_show_picture')
            _pop(fields, 'color')
        return fieldsets


@admin.register(Attribute)
class AttributeAdmin(TabbedTranslationAdmin):
    list_display = ('admin_title', 'title_ru', 'category', 'attr_type', 'slug', 'display_type', 'neighbor', 'order',)
    list_editable = ('order',)
    list_filter = ('attr_type', 'category', 'display_type',)
    ordering = ['-category', 'attr_type', 'order', 'id', ]
    suit_form_tabs = (
        ('default', 'Атрибут'),
        ('options', 'Варианты'),
    )
    fieldsets = (
        (None, {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('admin_title', 'title', 'slug', 'category', 'attr_type', 'neighbor',
                       # 'position', 'add_to_price',
                       'display_type', 'order',),
        }),
        ('Варианты', {
            'classes': ('suit-tab suit-tab-options',),
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
        if not obj or obj.attr_type != 'style':
            readonly_fields.append('neighbor')
        return readonly_fields


@admin.register(ExtraProduct)
class ExtraProductAdmin(TabbedTranslationAdmin):
    list_display = ('admin_title', 'title_ru', 'slug', 'order', 'show_attributes',)
    list_editable = ('order',)
    fieldsets = (
        ('Товар', {
            'fields': ('admin_title', 'title', 'slug', 'order',),
        }),
        ('Атрибуты', {
            'fields': ('attributes',),
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
    list_display = ('show_sex', 'title', 'slug', 'order', 'show_attributes', 'ozon_category_id', 'is_shown',)
    list_display_links = ('title',)
    list_editable = ('order', 'ozon_category_id', 'is_shown',)
    list_filter = ('sex', 'is_shown',)
    list_per_page = 200
    suit_form_tabs = (
        ('default', 'Категория'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
    )
    fieldsets = (
        ('Категория', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('sex', 'title', 'slug', 'title_yandex', 'ozon_category_id', 'order', 'is_shown',),
        }),
        ('Атрибуты', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('attributes',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',),
        }),
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
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


@admin.register(GiftWrapping)
class GiftWrappingAdmin(admin.ModelAdmin):
    list_display = ('show_name', 'price_rub', 'price_eur', 'price_usd',)
    list_display_links = None
    list_editable = ('price_rub', 'price_eur', 'price_usd',)
    fieldsets = (
        (None, {
            'fields': ('show_name', 'price_rub', 'price_eur', 'price_usd',),
        }),
    )
    readonly_fields = ('show_name',)

    def has_add_permission(self, request):
        if GiftWrapping.objects.count():
            return None
        return super(GiftWrappingAdmin, self).has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return None


# === Товары ===

class InStockFilter(SimpleListFilter):
    title = 'Кол-во товара на складе'
    parameter_name = 'in_stock'

    def lookups(self, request, model_admin):
        return (
            ('less_than_five', 'Меньше 5-ти'),
        )

    def queryset(self, request, queryset):
        return (queryset.filter(options__in_stock__lt=5).distinct() if self.value() == 'less_than_five'
                else queryset)


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
    suit_classes = 'suit-tab suit-tab-options'
    min_num = 1
    extra = 0


class ProductExtraOptionInline(ProductExtraOptionAdmin):
    model = ProductExtraOption
    form = ProductExtraOptionInlineForm
    fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)
    default_fields = ('title', 'vendor_code', 'price_rub', 'price_eur', 'price_usd', 'in_stock',)
    readonly_fields = ('extra_product',)
    suit_classes = 'suit-tab suit-tab-extra'
    min_num = 0
    extra = 0

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    # def get_fields(self, *args, **kwargs):
    #     fields = super(ProductExtraOptionInline, self).get_fields(*args, **kwargs)
    #     for field in fields:
    #         # избавляемся от динамических полей, оставшихся от других моделей
    #         if field not in self.default_fields:
    #             fields.pop(fields.index(field))
    #     return fields


class ProductPhotoInline(ProductPhotoAdmin):
    model = ProductPhoto
    form = ProductPhotoInlineForm
    formset = ProductPhotoInlineFormset
    fields = ('title', 'photo_f', 'order',)
    suit_classes = 'suit-tab suit-tab-photos'

    def get_extra(self, request, obj=None, **kwargs):
        extra = (0 if obj and obj.photos.count()
                 else 1)
        return extra


# class ProductVideoInline(TranslationInlineModelAdmin, admin.StackedInline):  # CompactInline
#     model = Video
#     fields = ('title', 'slug', 'video', 'cover', 'text', 'show_at_list')
#     prepopulated_fields = {'slug': ('title',)}
#     suit_classes = 'suit-tab suit-tab-video'
#     min_num = 0
#     extra = 1


@admin.register(Product)
class ProductAdmin(SortableAdminMixin, SalmonellaMixin, TabbedTranslationAdmin):
    change_categories_template = 'admin/catalog/product/change_categories.html'
    change_attributes_template = 'admin/catalog/product/change_attributes.html'

    def update_data(self, request, queryset):
        opts = Product._meta
        form = None
        count = queryset.count()
        count_label = choose_plural(count, ('товара', 'товаров', 'товаров'))

        queryset = queryset.select_related('photo_f').prefetch_related('options', 'extra_options', 'extra_options__extra_product')

        if 'apply' in request.POST:
            pass
            # form = UpdateProductsDataForm(request.POST)

            # if form.is_valid():
            #     delivery_price = form.cleaned_data['delivery_price']
            #     queryset.update(delivery_price=delivery_price)
            #     self.message_user(request, 'Delivery price of {0} {1} updated.'.format(count, count_label), messages.SUCCESS)
            #     return

        if not form:
            # prices = list(set(queryset.values_list('delivery_price', flat=True)))
            # initial_price = prices[0] if len(prices) == 1 else 0
            form = UpdateProductsDataForm(
                initial={
                    '_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME),
                    # 'delivery_price': initial_price,
                }
            )

        data = {
            'products': queryset, 'form': form,
            'count': count, 'count_label': count_label,
            'opts': opts, 'app_label': opts.app_label,
            'request': request,
        }
        data.update(csrf(request))
        return render_to_response('admin/catalog/product/update_data.html', data)

    update_data.short_description = 'Изменить товары массово'

    def change_categories_view(self, request, id, form_url='', extra_context=None):
        opts = Product._meta
        try:
            obj = Product.objects.get(pk=id)
        except (Product.DoesNotExist, ValueError) as e:
            print e
            raise Http404
        form = ChangeCategoriesForm(request.POST, instance=obj) if request.POST else ChangeCategoriesForm(instance=obj)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        if obj:
            old_categories = set(obj.categories.values_list('id', flat=True))

        if form.is_valid():
            new_categories = set([int(cat_id) for cat_id in form.cleaned_data['categories']])
            form.save()

            if new_categories != old_categories:
                obj.set_attributes_from_categories(new_categories)

            self.message_user(request,
                              mark_safe('''Категории у товара "<a href="/admin/catalog/product/{}/change/">{}</a>"
                                 изменены на "{}".'''.format(id, obj.__unicode__(), obj.list_categories(),)),
                              messages.SUCCESS)
            return HttpResponseRedirect('/admin/catalog/product/{}/change_attributes/'.format(id))

        preserved_filters = self.get_preserved_filters(request)
        form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)

        context = {
            'title': 'Изменить категории у товара %s' % obj,
            'has_change_permission': self.has_change_permission(request, obj),
            'form_url': form_url,
            'form': form,
            'opts': opts,
            'errors': form.errors,
            'app_label': opts.app_label,
            'original': obj,
        }
        context.update(extra_context or {})
        return render(request, self.change_categories_template, context)

    def change_attributes_view(self, request, id, form_url='', extra_context=None):
        opts = Product._meta
        try:
            obj = Product.objects.get(pk=id)
        except (Product.DoesNotExist, ValueError) as e:
            print e
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
            url(r'^(.+)/change_categories/$',
                wrap(self.change_categories_view),
                name='%s_%s_change_categories' % info),
            url(r'^(.+)/change_attributes/$',
                wrap(self.change_attributes_view),
                name='%s_%s_change_attributes' % info),
        ]
        super_urls = super(ProductAdmin, self).get_urls()
        return urls + super_urls

    actions = ['update_data', ]
    list_display = ('id', 'title', 'slug', 'list_categories', 'show', 'has_attrs', 'show_at_homepage',
                    'order_at_homepage', 'add_dt', 'vendor_code', 'get_in_stock', 'show_sale_percent',)
    list_display_links = ('id', 'title',)
    list_editable = ('order_at_homepage', 'vendor_code')
    list_filter = ('show', HasAttrsFilter, InStockFilter, 'show_at_homepage', 'add_dt', 'categories',
                   'is_on_sale', 'show_only_on_sale',)
    suit_list_filter_horizontal = ('show', 'show_at_homepage', 'categories', 'is_on_sale',)
    list_per_page = 400
    suit_form_tabs = (
        ('default', 'Товар'),
        ('also', 'Сопутствующие товары'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
        ('sale', 'Скидки'),
        ('options', 'Варианты товара'),
        ('photos', 'Фото'),
        # ('video', 'Видео'),
        ('extra', 'Дополнительные товары'),
    )
    suit_form_size = {
        'fields': {
            'text': apps.SUIT_FORM_SIZE_FULL,
            'seo_text': apps.SUIT_FORM_SIZE_FULL,
            # 'color': apps.SUIT_FORM_SIZE_SMALL,
        },
        # 'widgets': {
        #     'AutosizedTextarea': apps.SUIT_FORM_SIZE_XXX_LARGE,
        # },
    }
    form = ProductAdminForm
    fieldsets = (
        ('Товар', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('title', 'subtitle', 'slug', 'categories', 'vendor_code',
                       # 'photo', 'photo_f',
                       'photo_f',
                       ('price_rub', 'price_eur', 'price_usd',), 'text',),
        }),
        ('Настройки показа на сайте', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('show', 'show_at_yandex', 'show_at_homepage', 'order_at_homepage', 'ozone_type', 'add_dt',),
        }),
        ('Сопутствующие товары', {
            'classes': ('suit-tab suit-tab-also',),
            # 'fields': ('additional_products', 'associated_products', 'also_products',),
            'fields': ('associated_products', 'also_products',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam',),
        }),
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs',),
        }),
        ('Скидки', {
            'classes': ('suit-tab suit-tab-sale',),
            'fields': ('is_on_sale', 'sale_percent', 'show_only_on_sale',
                       'sale_price_rub', 'sale_price_eur', 'sale_price_usd',),
        }),
        ('Варианты товара', {
            'classes': ('suit-tab suit-tab-options',),
            'fields': ('options_instruction',),
        }),
        ('Фото', {
            'classes': ('suit-tab suit-tab-photos',),
            'fields': ('photos_instruction',),
        }),
        ('Дополнительные товары', {
            'classes': ('suit-tab suit-tab-extra',),
            'fields': ('extra_options_instruction',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('id', 'add_dt',
                       'options_instruction', 'extra_options_instruction', 'photos_instruction',
                       'show_categories', 'show_attributes',
                       'is_on_sale', 'sale_price_rub', 'sale_price_eur', 'sale_price_usd',)
    filter_vertical = ['categories', ]
    inlines = [ProductOptionInline, ProductPhotoInline,
               # ProductVideoInline,
               ProductExtraOptionInline, ]
    raw_id_fields = ('associated_products', 'also_products',)
    search_fields = ['title', 'vendor_code', 'subtitle', ]

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.prefetch_related('categories', 'options')
        return qs

    def get_fieldsets(self, request, obj=None):
        """
        Если объект уже создан, вместо таба с инструкциями будут табы с инлайнами.
        Также вместо поля выбора категории показываем ридонли-поле с ссылкой на страниу выбора
        """
        fieldsets = list(super(ProductAdmin, self).get_fieldsets(request, obj))
        if obj and obj.id:
            fieldsets[0][1]['fields'][18] = 'show_categories'  # меняем 'categories' на 'show_categories'

            # удаляем вкладки с инструкциями (вместо них будут вкладки с инлайнами)
            del fieldsets[11]  # варианты товара
            del fieldsets[11]  # фото
            if obj.extra_options.count():
                del fieldsets[11]  # дополнительные товары
        else:
            fieldsets[0][1]['fields'][18] = 'categories'  # меняем 'show_categories' на 'categories'
        return fieldsets

    def get_inline_instances(self, request, obj=None):
        """
        Если объект уже создан (а главное, выбрана категория), показываем инлайны
        """
        s = super(ProductAdmin, self).get_inline_instances(request, obj)
        if not obj:
            # s = s[2:3]
            s = []
        elif not obj.extra_options.count():
            # s = s[:3]
            s = s[:2]
        return s

    def get_readonly_fields(self, request, obj=None):
        """
        Если объект уже создан, не даем менять категории (только на отдельной странице)
        """
        readonly_fields = list(super(ProductAdmin, self).get_readonly_fields(request, obj))
        if obj:
            readonly_fields.append('categories')
        return readonly_fields

    def save_model(self, request, obj, form, change):
        """
        Заполняем атрибуты у товара сразу после создания из его категорий
        """
        set_attributes = False
        if not obj.id:
            set_attributes = True
        s = super(ProductAdmin, self).save_model(request, obj, form, change)
        if set_attributes:
            categories_ids = form.cleaned_data.get('categories')
            obj.set_attributes_from_categories(categories_ids)
        return s

    def save_formset(self, request, form, formset, change):
        """
        Обновляем поле attrs у товара после сохранения всех его вариантов
        """
        s = super(ProductAdmin, self).save_formset(request, form, formset, change)
        if formset.model == ProductOption:
            formset.instance.set_attrs()
        return s


class ProductTabSectionInline(TranslationStackedInline):
    model = ProductTabSection
    fields = ('title', 'text', 'show', 'order',)
    suit_classes = 'suit-tab suit-tab-accordion'
    extra = 0


@admin.register(ProductTab)
class ProductTabAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'order', 'show_sections_count',)
    list_editable = ('order',)
    suit_form_tabs = (
        ('default', 'Вкладка'),
        ('accordion', 'Секции'),
    )
    fieldsets = (
        ('Вкладка', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('title', 'text', 'order',),
        }),
    )
    inlines = [ProductTabSectionInline, ]

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductTabAdmin, self).get_queryset(*args, **kwargs)
        return qs.prefetch_related('sections')


# === Спец.предложения ===

@admin.register(SpecialOfferCategory)
class SpecialOfferCategoryAdmin(admin.ModelAdmin):
    list_display = ('show_title', 'is_active', 'price_rub', 'price_eur', 'price_usd',)
    readonly_fields = ('price_eur', 'price_usd',)
    fields = ('title', 'price_rub', 'price_eur', 'price_usd', 'is_active',)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.id == 1:
            return None
        return (None if (obj and obj.id == 1)
                else super(SpecialOfferCategoryAdmin, self).has_delete_permission(request, obj))


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ('product', 'category', 'discount', 'is_active',)
    list_editable = ('discount', 'is_active',)
    list_filter = ('category',)
    form = SpecialOfferAdminForm
    raw_id_fields = ('product',)

    def get_queryset(self, *args, **kwargs):
        qs = super(SpecialOfferAdmin, self).get_queryset(*args, **kwargs)
        return qs.select_related('product', 'category')
