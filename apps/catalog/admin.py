# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import Category, Product
from .translation import *


@admin.register(Category)
class CategoryAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'title_en', 'sex', 'order',)
    list_editable = ('title_en', 'order',)
    list_filter = ('sex',)
    fieldsets = (
        (None, {
            'fields': ('title', 'sex', 'order',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )


@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    list_display = ('id', 'title', 'product_type', 'show_categories', 'show', 'show_at_homepage',
                    'order_at_homepage', 'add_dt', 'in_stock',)
    list_editable = ('order_at_homepage', 'in_stock',)
    list_filter = ('product_type', 'show', 'show_at_homepage', 'add_dt', 'categories',)
    list_per_page = 200
    fieldsets = (
        (None, {
            'fields': ('id', 'title', 'subtitle', 'categories', 'vendor_code', 'photo',
                       'price_rub', 'price_eur', 'price_usd', 'text', 'in_stock',),
        }),
        ('Настройки показа на сайте', {
            'fields': ('show', 'show_at_homepage', 'order_at_homepage', 'add_dt',),
        }),
        ('Дополнительные товары', {
            'fields': ('additional_products', 'associated_products', 'also_products',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    readonly_fields = ('id', 'add_dt',)
    raw_id_fields = ('additional_products', 'associated_products', 'also_products',)
    search_fields = ['title', 'subtitle', 'text', ]
    ordering = ('-product_type', '-id',)
