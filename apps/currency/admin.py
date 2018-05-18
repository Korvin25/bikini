# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .admin_forms import EURAdminForm, USDAdminForm
from .models import EUR, USD


@admin.register(EUR)
class EURAdmin(SingletonModelAdmin):
    form = EURAdminForm
    fieldsets = (
        (None, {
            'fields': ('rate', 'update_dt',)
        }),
    )
    readonly_fields = ('update_dt',)


@admin.register(USD)
class USDAdmin(SingletonModelAdmin):
    form = USDAdminForm
    fieldsets = (
        (None, {
            'fields': ('rate', 'update_dt',)
        }),
    )
    readonly_fields = ('update_dt',)
