# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin

from .models import Video, HomepageSlider, Page
from .translation import *


@admin.register(Video)
class VideoAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'title_en', 'video', 'video_id', 'order', 'cover', 'product', 'add_dt',)
    list_editable = ('title_en', 'order',)
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


@admin.register(HomepageSlider)
class HomepageSliderAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'title_en', 'slider_type', 'order',
                    'link', 'link_text', 'cover', 'video', 'video_id', 'add_dt',)
    list_editable = ('title_en', 'order',)
    list_filter = ('slider_type',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slider_type', 'description', 'link', 'link_text',
                       'cover', 'video', 'video_id', 'order', 'add_dt',),
        }),
    )
    readonly_fields = ('video_id', 'add_dt',)
    search_fields = ['title', 'description', 'link_text', ]

    def has_delete_permission(self, request, obj=None):
        if HomepageSlider.objects.count() < 2:
            return None
        return super(HomepageSliderAdmin, self).has_delete_permission(request, obj)


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
