# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from modeltranslation.admin import TabbedTranslationAdmin
from solo.admin import SingletonModelAdmin

from ..core.admin import ImageThumbAdminMixin
from .models import Settings, SEOSetting  # , Setting, VisualSetting
from .translation import *  # noqa


def MetatagModelAdmin(cls=None):

    def decorator(cls):
        cls.fieldsets += (
            ('SEO', {
                'classes': ('collapse',),
                'fields': ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)
            }),
            ('SEO: Санкт-Петербург', {
                'classes': ('collapse',),
                'fields': ('meta_title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',)
            }),
            ('SEO: Новосибирск', {
                'classes': ('collapse',),
                'fields': ('meta_title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',)
            }),
            ('SEO: Самара', {
                'classes': ('collapse',),
                'fields': ('meta_title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',)
            }),
            ('SEO: Сочи', {
                'classes': ('collapse',),
                'fields': ('meta_title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',)
            }),
            ('SEO: Симферополь', {
                'classes': ('collapse',),
                'fields': ('meta_title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',)
            }),
            ('SEO: Севастополь', {
                'classes': ('collapse',),
                'fields': ('meta_title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',)
            }),
        )
        cls.search_fields += ['meta_title', 'meta_desc', 'meta_keyw', 'h1', ]
        return cls

    if cls is None:
        return decorator
    else:
        return decorator(cls)


@admin.register(Settings)
class SettingsAdmin(ImageThumbAdminMixin, SingletonModelAdmin, TabbedTranslationAdmin):
    fieldsets = (
        ('Email для обратной связи', {
            'fields': ('feedback_email', 'orders_email',)
        }),
        ('Контент на страницах', {
            'fields': ('title_mailing', 'title_suffix', 'telegram_login', 'whatsapp_phone', 'phone',)
        }),
        ('Код социальных виджетов на главной', {
            'fields': ('ig_widget', 'vk_widget', 'fb_widget', 'tw_widget',)
        }),
        ('Robots.txt и метрика', {
            'fields': ('robots_txt', 'ym_code', 'ga_code',)
        }),
        ('Cookies-предупреждения', {
            'fields': ('cookies_notify', 'cookies_alert', 'cookies_cart',)
        }),
        ('Акции в каталоге', {
            'fields': ('catalog_special_banner', 'catalog_special_text', 'catalog_special_order',)
        }),
        ('Процент для маркетплейс', {
            'fields': ('percent_marketplays',)
        }),

    )


# @admin.register(Setting)
# class SettingAdmin(TabbedTranslationAdmin):
#     list_display = ('key', 'value', 'description',)
#     fieldsets = (
#         (None, {
#             'fields': ('key', 'value', 'description',)
#         }),
#     )

#     def get_readonly_fields(self, request, obj=None):
#         fields = list(super(SettingAdmin, self).get_readonly_fields(request, obj))
#         if obj:
#             fields.append('key')
#         return fields

#     def has_delete_permission(self, request, obj=None):
#         return None


# @admin.register(VisualSetting)
# class VisualSettingAdmin(TabbedTranslationAdmin):
#     list_display = ('key', 'description',)
#     fieldsets = (
#         (None, {
#             'fields': ('key', 'value', 'description',)
#         }),
#     )

#     def get_readonly_fields(self, request, obj=None):
#         fields = list(super(VisualSettingAdmin, self).get_readonly_fields(request, obj))
#         if obj:
#             fields.append('key')
#         return fields

#     def has_delete_permission(self, request, obj=None):
#         return None


@admin.register(SEOSetting)
class SEOSettingAdmin(TabbedTranslationAdmin):
    list_display = ('key', 'description', 'show_meta_title', 'show_meta_desc', 'show_meta_keyw',
                    'show_h1', 'has_seo_text',)
    list_display_links = ('key', 'description',)
    list_per_page = 50
    suit_form_tabs = (('default', 'SEO-настройка'), ('regions', 'SEO по регионам'),)
    fieldsets = (
        ('SEO-настройка', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('key', 'description', 'title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)
        }),
        ('Санкт-Петербург', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_spb', 'meta_desc_spb', 'meta_keyw_spb', 'h1_spb', 'seo_text_spb',)
        }),
        ('Новосибирск', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_nsk', 'meta_desc_nsk', 'meta_keyw_nsk', 'h1_nsk', 'seo_text_nsk',)
        }),
        ('Самара', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_sam', 'meta_desc_sam', 'meta_keyw_sam', 'h1_sam', 'seo_text_sam',)
        }),
        ('Сочи', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_sch', 'meta_desc_sch', 'meta_keyw_sch', 'h1_sch', 'seo_text_sch',),
        }),
        ('Симферополь', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_smf', 'meta_desc_smf', 'meta_keyw_smf', 'h1_smf', 'seo_text_smf',),
        }),
        ('Севастополь', {
            'classes': ('suit-tab', 'suit-tab-regions',),
            'fields': ('title_svs', 'meta_desc_svs', 'meta_keyw_svs', 'h1_svs', 'seo_text_svs',),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(SEOSettingAdmin, self).get_readonly_fields(request, obj))
        if obj:
            fields.append('key')
        return fields

    def has_delete_permission(self, request, obj=None):
        return None
