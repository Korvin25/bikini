# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from embed_video.admin import AdminVideoMixin
# from jet.admin import CompactInline
from modeltranslation.admin import TranslationInlineModelAdmin, TabbedTranslationAdmin

from filer.admin import FolderAdmin as _FolderAdmin
from filer.models import Folder

from .admin_forms import VideoAdminForm
from .models import Video, Page, Menu, MenuItem
from .translation import *


admin.site.site_header = 'Bikinimini.ru'


class FolderAdmin(_FolderAdmin):
    order_by_file_fields = ('-uploaded_at', 'original_filename', )


admin.site.unregister(Folder)
admin.site.register(Folder, FolderAdmin)


@admin.register(Video)
class VideoAdmin(AdminVideoMixin, TabbedTranslationAdmin):
    list_display = ('title', 'slug', 'video', 'order', 'cover', 'product', 'add_dt',)
    list_editable = ('order',)
    list_filter = ('show_at_list',)
    # form = VideoAdminForm
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'video', 'cover', 'text', 'product', 'show_at_list', 'order', 'add_dt',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('add_dt',)
    raw_id_fields = ('product',)
    search_fields = ['title', 'text', 'video', ]


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'slug', 'image', 'order',)
    list_editable = ('order',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'image', 'image_attributes', 'text', 'order',),
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'seo_text',),
        }),
    )
    search_fields = ['title', 'slug', 'text', ]


class MenuItemInline(TranslationInlineModelAdmin, admin.StackedInline):  # CompactInline
    model = MenuItem
    fields = ('label', 'link', 'target_blank', 'order',)
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
