# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.admin.filters import SimpleListFilter
from django.utils import timezone

from jet.admin import CompactInline
from modeltranslation.admin import TabbedTranslationAdmin

from .models import Banner, BannerTextLine, PromoBanner, PromoBannerGirl
from .translation import *


class IsPublishedNow(SimpleListFilter):
    """
    Дополнительный фильтр для баннеров в админке
    """
    title = 'Размещены сейчас'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Нет'),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        published_filter = {
            'start_datetime__lte': now,
            'end_datetime__gte': now,
            'show': True,
        }

        if self.value() == 'yes':
            return queryset.filter(**published_filter)

        if self.value() == 'no':
            return queryset.exclude(**published_filter)


class BannerTextLineInline(CompactInline):
    model = BannerTextLine
    fields = ('line_ru', 'line_en', 'line_de', 'line_fr', 'line_it', 'line_es', 'big', 'order',)
    extra = 1


@admin.register(Banner)
class BannerAdmin(TabbedTranslationAdmin):
    list_display = ('id', 'title_ru', 'image', 'url', 'location', 'show', 'target_blank',
                    'show_has_text', 'show_has_button',
                    'start_datetime', 'end_datetime',)
                    # 'shows', 'clicks',)
    list_display_links = ('id', 'title_ru',)
    list_filter = ('location', 'show', IsPublishedNow)
    fieldsets = (
        (None, {
            'fields': ('title', 'image', 'location',
                       'url', 'button_text', 'target_blank',
                       'show', 'start_datetime', 'end_datetime',)
        }),
    )
    inlines = [BannerTextLineInline, ]


class PromoBannerGirlInline(admin.TabularInline):
    model = PromoBannerGirl
    exclude = ('name',)
    extra = 0
    min_length = 1


@admin.register(PromoBanner)
class PromoBannerAdmin(TabbedTranslationAdmin):
    list_display = ('id', 'title', 'is_enabled', 'link', 'link_text', 'cover', 'add_dt',)
    list_display_links = ('title',)
    list_filter = ('is_enabled',)
    fieldsets = (
        (None, {
            'fields': (# 'banner_type', 
                       'title',
                       'description_h1', 'description_picture', 'description_picture_alt', 'description_p',
                       'link', 'link_text', 'is_enabled', 'add_dt',),
        }),
        ('Обложка', {
            'fields': ('cover',),
        }),
    )
    readonly_fields = ('video_id', 'add_dt',)
    inlines = [PromoBannerGirlInline, ]
    # search_fields = ['title', 'description', 'link_text', ]
    search_fields = ['title', 'description_h1', 'description_p', 'link_text', ]

    def has_delete_permission(self, request, obj=None):
        if PromoBanner.objects.count() < 2:
            return None
        return super(PromoBannerAdmin, self).has_delete_permission(request, obj)
