# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin
from modeltranslation.admin import TabbedTranslationAdmin

from .models import DeliveryMethod, PaymentMethod, Cart
from .translation import *


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = ('title', 'price_rub', 'price_eur', 'price_usd',)
    list_editable = ('price_rub', 'price_eur', 'price_usd',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = ('title',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'checked_out', 'is_order_with_discount', 'checkout_date', 'summary', 'country',
                    'show_delivery_method', 'show_payment_method', 'status',)
    list_display_links = ('id', 'profile',)
    list_filter = ('status', 'delivery_method', 'payment_method',)
    list_per_page = 200
    fieldsets = (
        ('Общее', {
            'fields': ('id', 'profile', 'status',)
        }),
        ('Данные из формы', {
            'fields': ('country', 'city', 'address', 'phone', 'name',
                       'delivery_method', 'payment_method', 'additional_info',)
        }),
        ('Список позиций', {
            'fields': ('show_items',)
        }),
    )
    readonly_fields = ('id', 'profile', 'show_items',)

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    def get_queryset(self, *args, **kwargs):
        qs = super(CartAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.filter(checked_out=True)
        return qs
