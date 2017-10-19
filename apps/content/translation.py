# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import Video, HomepageSlider, Page


class VideoTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


class HomepageSliderTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'link', 'link_text',)


class PageTranslationOptions(TranslationOptions):
    fields = ('title', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'seo_text',)


translator.register(Video, VideoTranslationOptions)
translator.register(HomepageSlider, HomepageSliderTranslationOptions)
translator.register(Page, PageTranslationOptions)
