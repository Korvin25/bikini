# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, translator, TranslationOptions

from .models import Category, Post


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title', 'slug',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)


@register(Post)
class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'description', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'h1', 'seo_text',)
