# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import TranslationOptions


class TitleTranslationOptions(TranslationOptions):
    fields = ('title',)


class DescriptionTranslationOptions(TranslationOptions):
    fields = ('description',)


class TextTranslationOptions(TranslationOptions):
    fields = ('text',)


class TitleTextTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)


class MetatagTranslationOptions(TranslationOptions):
    fields = ('meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


class MetatagTitleTranslationOptions(TranslationOptions):
    fields = ('title', 'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)
