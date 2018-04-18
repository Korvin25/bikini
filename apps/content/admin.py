# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from embed_video.admin import AdminVideoMixin
from filer.models import Folder, File, Image
from modeltranslation.admin import TranslationInlineModelAdmin, TabbedTranslationAdmin, TranslationStackedInline
from paypal.standard.ipn.models import PayPalIPN

from .admin_filer import CustomFolderAdmin, CustomFileAdmin, CustomImageAdmin
from .admin_forms import MenuItemAdminForm
from .models import Video, Page, Menu, MenuItem
from .translation import *


admin.site.site_header = 'Bikinimini.ru'


admin.site.unregister(PayPalIPN)
admin.site.unregister(Folder)
admin.site.unregister(File)
admin.site.unregister(Image)
admin.site.register(Folder, CustomFolderAdmin)
admin.site.register(File, CustomFileAdmin)
admin.site.register(Image, CustomImageAdmin)


@admin.register(Video)
class VideoAdmin(AdminVideoMixin, TabbedTranslationAdmin):
    list_display = ('title', 'slug', 'video', 'order', 'cover', 'product', 'post', 'add_dt',)
    list_editable = ('order',)
    list_filter = ('show_at_list', 'add_dt',)
    suit_form_tabs = (
        ('default', 'Видео'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
    )
    fieldsets = (
        ('Видео', {
            'classes': ('suit-tab suit-tab-default',),
            'fields': ('title', 'slug', 'video', 'cover', 'text', 'product', 'post', 'show_at_list', 'order', 'add_dt',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('add_dt',)
    raw_id_fields = ('product', 'post',)
    search_fields = ['title', 'text', 'video', ]


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    # list_display = ('title_ru', 'slug', 'image', 'order',)
    list_display = ('title_ru', 'slug', 'order',)
    list_editable = ('order',)
    suit_form_tabs = (
        ('default', 'Страница'),
        ('seo', 'SEO'),
        ('seo-regions', 'SEO (регионы)'),
    )
    fieldsets = (
        ('Страница', {
            'classes': ('suit-tab suit-tab-default',),
            # 'fields': ('title', 'slug', 'image', 'image_attributes', 'text', 'order',),
            'fields': ('title', 'slug', 'text', 'order',),
        }),
        ('SEO', {
            'classes': ('suit-tab suit-tab-seo',),
            'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',),
        }),
        ('SEO: Санкт-Петербург', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',),
        }),
        ('SEO: Новосибирск', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',),
        }),
        ('SEO: Самара', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',),
        }),
    )
    search_fields = ['title', 'slug', 'text', ]


class MenuItemInline(TranslationStackedInline):  # CompactInline
    model = MenuItem
    form = MenuItemAdminForm
    fields = ('label', 'page', 'link', 'target_blank', 'order',)
    extra = 0


@admin.register(Menu)
class MenuAdmin(TabbedTranslationAdmin):
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
