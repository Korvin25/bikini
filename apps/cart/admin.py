# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'checked_out', 'checkout_date', 'summary', 'status',)
    list_display_links = ('id', 'profile',)
    list_filter = ('status',)
    list_per_page = 200
    fieldsets = (
        ('Общее', {
            'fields': ('id', 'profile', 'status',)
        }),
        ('Данные из формы', {
            'fields': ('country', 'city', 'address', 'phone', 'name', 'additional_info',)
        }),
        ('Список товаров', {
            'fields': ('show_items',)
        }),
    )
    readonly_fields = ('id', 'profile', 'show_items',)

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None
