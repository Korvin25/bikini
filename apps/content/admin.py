# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from jet.admin import CompactInline
from modeltranslation.admin import TabbedTranslationAdmin

from .admin_forms import VideoAdminForm
from .models import Video, Page, Menu, MenuItem
from .translation import *


@admin.register(Video)
class VideoAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'title_en', 'video', 'video_id', 'order', 'cover', 'product', 'add_dt',)
    list_editable = ('title_en', 'order',)
    form = VideoAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'video', 'video_id', 'cover', 'text', 'product', 'order', 'add_dt',),
        }),
        # ('SEO', {
        #     'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        # }),
    )
    readonly_fields = ('video_id', 'add_dt',)
    raw_id_fields = ('product',)
    search_fields = ['title', 'text', 'video', ]


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'title_en', 'slug', 'image', 'order',)
    list_editable = ('title_en', 'order',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'image', 'image_attributes', 'text', 'order',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    search_fields = ['title', 'slug', 'text', ]


class MenuItemInline(CompactInline):
    model = MenuItem
    fields = ('label_ru', 'label_en', 'link_ru', 'link_en', 'target_blank', 'order',)
    extra = 0


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug',),
        }),
    )
    inlines = [MenuItemInline, ]

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(MenuAdmin, self).get_readonly_fields(request, obj))
        if obj:
            fields.append('title')
            fields.append('slug')
        return fields

    def has_delete_permission(self, request, obj=None):
        return None
