# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, TranslationOptions

from .models import Video, Page, PageAccordionSection, MenuItem, Menu


@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


@register(Page)
class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


@register(PageAccordionSection)
class PageAccordionSectionTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


@register(MenuItem)
class MenuItemTranslationOptions(TranslationOptions):
    fields = ('label', 'link',)


@register(Menu)
class MenuTranslationOptions(TranslationOptions):
    fields = ()
