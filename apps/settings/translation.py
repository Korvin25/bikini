# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import Setting, VisualSetting, SEOSetting


class SettingTranslationOptions(TranslationOptions):
    fields = ('value',)


class VisualSettingTranslationOptions(TranslationOptions):
    fields = ('value',)


class SEOSettingTranslationOptions(TranslationOptions):
    fields = ('description', 'title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


translator.register(Setting, SettingTranslationOptions)
translator.register(VisualSetting, VisualSettingTranslationOptions)
translator.register(SEOSetting, SEOSettingTranslationOptions)
