# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
# from django.db.models import Count, Q
# from django.db.models import CharField, Case, Value, When
from django.utils.safestring import mark_safe

from adminsortable2.admin import SortableAdminMixin
from modeltranslation.admin import TabbedTranslationAdmin
from rangefilter.filter import DateTimeRangeFilter

from ..analytics.admin_utils import CountryFilter, TrafficSourceFilter, traffic_source_to_str
from .models import DeliveryMethod, PaymentMethod, Cart
from .translation import *  # noqa


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = ('title', 'short_title', 'price_rub', 'price_eur', 'price_usd',
                    'show_languages', 'is_enabled', 'show_payment_methods',)
    list_editable = ('short_title', 'price_rub', 'price_eur', 'price_usd',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(SortableAdminMixin, TabbedTranslationAdmin):
    list_display = ('title', 'short_title', 'payment_type', 'show_languages',
                    'is_enabled', 'show_delivery_methods',)
    list_editable = ('short_title',)
    filter_horizontal = ['delivery_methods',]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'profile', 'checked_out', 'is_order_with_discount', 'yoo_paid', 'robokassa_paid', 'paypal_paid',
                    'checkout_date', 'show_delivery_method', 'show_payment_method',
                    'admin_show_summary', 'show_status', 'count', 'country', 'city', 'show_traffic_source', 'show_num_orders',)
    list_display_links = ('__unicode__', 'profile',)
    list_filter = ('status', 'yoo_status', 'paypal_status', 'delivery_method', 'payment_method',
                   ('checkout_date', DateTimeRangeFilter),
                   CountryFilter, 'city', TrafficSourceFilter)
    suit_list_filter_horizontal = (CountryFilter, 'city', TrafficSourceFilter,)
    list_per_page = 200
    fieldsets = (
        ('Общее', {
            'fields': ('id', 'profile_with_link', 'checked_out', 'checkout_date', 'payment_date', 'status',)
        }),
        ('Данные из формы', {
            'fields': ('country', 'city', 'postal_code', 'address', 'phone', 'name',
                       'delivery_method', 'payment_method', 'additional_info',)
        }),
        ('YooKassa', {
            'fields': ('yoo_id', 'life_pay_id', 'yoo_status', 'yoo_paid', 'yoo_redirect_url', 'yoo_test',)
        }),
        ('RoboKassa', {
            'fields': ('robokassa_id', 'robokassa_status', 'robokassa_paid', 'robokassa_url', 'robokassa_signature')
        }),
        ('PayPal', {
            'fields': ('paypal_txn_id', 'paypal_status', 'paypal_paid', 'paypal_ipn_obj',)
        }),
        ('Яндекс.Метрика', {
            'fields': ('ym_client_id', 'ym_source', 'ym_source_detailed',)
        }),
        ('Список позиций', {
            'fields': ('show_items',)
        }),
    )
    readonly_fields = ['id', 'profile_with_link', 'show_items',]
    readonly_fields += ['country', 'city', 'postal_code', 'address', 'phone', 'name',
                        # 'delivery_method', 'payment_method',
                        'checked_out', 'checkout_date', 'payment_date',
                        'yoo_id', 'life_pay_id', 'yoo_status', 'yoo_paid', 'yoo_redirect_url', 'yoo_test',
                        'paypal_txn_id', 'paypal_status', 'paypal_paid', 'paypal_ipn_obj',
                        'ym_client_id', 'ym_source', 'ym_source_detailed',
                        'additional_info', 'robokassa_id', 'robokassa_status', 'robokassa_paid', 'robokassa_url', 'robokassa_signature']
    search_fields = ['id', 'country', 'city', 'profile__name',
                     'ym_source', 'ym_source_detailed', 'ym_client_id', ]

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    def get_queryset(self, *args, **kwargs):
        qs = super(CartAdmin, self).get_queryset(*args, **kwargs)
        qs = qs.prefetch_related('profile', 'cartitem_set', 'certificatecartitem_set').filter(checked_out=True)
        # qs = qs.annotate(Count('profile__cart', 'dawawd', Case(When(checked_out='True', then=1))))
        return qs

    def show_traffic_source(self, obj):
        return traffic_source_to_str(obj)
    show_traffic_source.short_description = mark_safe('Источник&nbsp;трафика')

    def show_num_orders(self, obj):
        # return obj.profile__cart__count
        return obj.profile.orders_num if obj.profile else '-'
    show_num_orders.short_description = 'Количество заказов'
