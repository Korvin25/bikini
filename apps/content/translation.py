# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, translator, TranslationOptions

from ..core.translation import TitleTranslationOptions
from .models import Video, Page, MenuItem


@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    fields = ('label', 'link',)
