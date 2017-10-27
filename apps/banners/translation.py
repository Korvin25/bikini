# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from .models import Banner, BannerTextLine, PromoBanner


class BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'image', 'url', 'button_text',)


class BannerTextLineTranslationOptions(TranslationOptions):
    fields = ('line',)


class PromoBannerTranslationOptions(TranslationOptions):
    fields = ('description_h1', 'description_picture_alt', 'description_p',
              'link', 'link_text',)


translator.register(Banner, BannerTranslationOptions)
translator.register(BannerTextLine, BannerTextLineTranslationOptions)
translator.register(PromoBanner, PromoBannerTranslationOptions)
