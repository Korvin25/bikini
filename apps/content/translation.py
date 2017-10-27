# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from ..core.translation import TitleTranslationOptions
from .models import Video, Page, Menu, MenuItem


class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'seo_text',)


class MenuItemTranslationOptions(TranslationOptions):
    fields = ('label', 'link',)


translator.register(Video, VideoTranslationOptions)
translator.register(Page, PageTranslationOptions)
# translator.register(Menu, TitleTranslationOptions)
translator.register(MenuItem, MenuItemTranslationOptions)
