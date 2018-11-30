# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, TranslationOptions

from .models import Settings, Setting, VisualSetting, SEOSetting


@register(Settings)
class SettingsTranslationOptions(TranslationOptions):
    fields = ('title_suffix', 'phone', 'telegram_login',
              'cookies_notify', 'cookies_alert', 'cookies_cart',
              'catalog_special_text',)


@register(Setting)
class SettingTranslationOptions(TranslationOptions):
    fields = ('value',)


@register(VisualSetting)
class VisualSettingTranslationOptions(TranslationOptions):
    fields = ('value',)


@register(SEOSetting)
class SEOSettingTranslationOptions(TranslationOptions):
    fields = ('description', 'title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)
