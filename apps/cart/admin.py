# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import DeliveryMethod, PaymentMethod, Cart
from .translation import *


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = ('title', 'short_title', 'price_rub', 'price_eur', 'price_usd',
                    'is_enabled', 'show_payment_methods',)
    list_editable = ('short_title', 'price_rub', 'price_eur', 'price_usd',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    # list_display = ('title', 'short_title', 'is_paypal', 'is_enabled',)
    list_display = ('title', 'short_title', 'is_enabled', 'show_delivery_methods',)
    list_editable = ('short_title',)
    exclude = ('is_paypal',)
    filter_horizontal = ['delivery_methods', ]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'profile', 'checked_out', 'is_order_with_discount', 'checkout_date',
                    'admin_show_summary', 'count', 'country', 'city',
                    'show_delivery_method', 'show_payment_method', 'status',)
    list_display_links = ('__unicode__', 'profile',)
    list_filter = ('status', 'delivery_method', 'payment_method',)
    list_per_page = 200
    fieldsets = (
        ('Общее', {
            'fields': ('id', 'profile_with_link', 'status',)
        }),
        ('Данные из формы', {
            'fields': ('country', 'city', 'address', 'phone', 'name',
                       'delivery_method', 'payment_method', 'additional_info',)
        }),
        ('Список позиций', {
            'fields': ('show_items',)
        }),
    )
    readonly_fields = ['id', 'profile_with_link', 'show_items',]
    readonly_fields += ['country', 'city', 'address', 'phone', 'name',
                       # 'delivery_method', 'payment_method',
                       'additional_info',]

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    def get_queryset(self, *args, **kwargs):
        qs = super(CartAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.prefetch_related('cartitem_set', 'certificatecartitem_set').filter(checked_out=True)
        return qs
