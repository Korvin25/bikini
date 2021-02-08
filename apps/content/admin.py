# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from embed_video.admin import AdminVideoMixin
from filer.models import Folder, File, Image
from modeltranslation.admin import TabbedTranslationAdmin, TranslationStackedInline
from paypal.standard.ipn.models import PayPalIPN

from .admin_filer import CustomFolderAdmin, CustomFileAdmin, CustomImageAdmin
from .admin_forms import MenuItemAdminForm
from .models import Video, Page, PageAccordionSection, Menu, MenuItem
from .translation import *  # noqa


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
    list_display = ('title', 'slug', 'video', 'order', 'cover', 'show_products', 'post', 'add_dt',)
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
            'fields': ('title', 'slug', 'video', 'cover', 'text', 'products', 'post', 'show_at_list', 'order', 'add_dt',),
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
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('add_dt',)
    raw_id_fields = ('products', 'post',)
    search_fields = ['title', 'text', 'video', ]

    def save_model(self, request, obj, form, change):
        s = super(VideoAdmin, self).save_model(request, obj, form, change)
        obj.update_video_cover()
        return s

    def get_queryset(self, *args, **kwargs):
        qs = super(VideoAdmin, self).get_queryset(*args, **kwargs)
        return qs.prefetch_related('products')


class PageAccordionSectionInline(TranslationStackedInline):
    model = PageAccordionSection
    fields = ('title', 'text', 'order',)
    suit_classes = 'suit-tab suit-tab-accordion'
    extra = 0


@admin.register(Page)
class PageAdmin(TabbedTranslationAdmin):
    # list_display = ('title_ru', 'slug', 'image', 'order',)
    list_display = ('title_ru', 'slug', 'order',)
    list_editable = ('order',)
    suit_form_tabs = (
        ('default', 'Страница'),
        ('accordion', 'Секции (аккордеон)'),
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
        ('SEO: Сочи', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('SEO: Симферополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('SEO: Севастополь', {
            'classes': ('suit-tab suit-tab-seo-regions',),
            'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )
    inlines = [PageAccordionSectionInline, ]
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
