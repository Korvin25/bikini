# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import CallbackOrder


@admin.register(CallbackOrder)
class CallbackOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'datetime', 'name', 'phone', 'profile',)
    list_display_links = ('id', 'datetime',)
    list_per_page = 200
    fieldsets = (
        ('Данные о заказе', {
            'fields': ('datetime', 'id',)
        }),
        ('Данные из формы', {
            'fields': ('profile', 'name', 'phone',)
        }),
    )
    search_fields = ['profile__email', 'name', 'phone', ]
    readonly_fields = ('id', 'datetime', 'profile', 'name', 'phone',)

    def has_add_permission(self, request):
        return False
