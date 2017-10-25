# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import Banner, BannerTextLine


class BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'image', 'url', 'button_text',)


class BannerTextLineTranslationOptions(TranslationOptions):
    fields = ('line',)


translator.register(Banner, BannerTranslationOptions)
translator.register(BannerTextLine, BannerTextLineTranslationOptions)
