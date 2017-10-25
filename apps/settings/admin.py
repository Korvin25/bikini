# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import Setting, VisualSetting, SEOSetting
from .translation import *


def MetatagModelAdmin(cls=None):

    def decorator(cls):
        cls.fieldsets += (
            ('SEO', {
                'classes': ('collapse',),
                'fields': ('meta_title', 'meta_desc', 'meta_keyw',)
            }),
        )
        cls.search_fields += ['meta_title', 'meta_desc', 'meta_keyw', ]
        return cls

    if cls is None:
        return decorator
    else:
        return decorator(cls)


@admin.register(Setting)
class SettingAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'value', 'description',)
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(SettingAdmin, self).get_readonly_fields(request, obj))
        if obj:
            fields.append('key')
        return fields

    def has_delete_permission(self, request, obj=None):
        return None


@admin.register(VisualSetting)
class VisualSettingAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'description',)
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'description',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(VisualSettingAdmin, self).get_readonly_fields(request, obj))
        if obj:
            fields.append('key')
        return fields

    def has_delete_permission(self, request, obj=None):
        return None


@admin.register(SEOSetting)
class SEOSettingAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'description', 'show_meta_title', 'show_meta_desc', 'show_meta_keyw', 'has_seo_text',)
    list_display_links = ('key', 'description',)
    list_per_page = 50
    fieldsets = (
        (None, {
            'fields': ('key', 'description', 'title', 'meta_desc', 'meta_keyw', 'seo_text',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(SEOSettingAdmin, self).get_readonly_fields(request, obj))
        if obj:
            fields.append('key')
        return fields

    def has_delete_permission(self, request, obj=None):
        return None
