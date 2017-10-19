# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator, TranslationOptions

from ..core.translation import MetatagTitleTranslationOptions
from .models import Category, Product


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'seo_text',)


translator.register(Category, MetatagTitleTranslationOptions)
translator.register(Product, ProductTranslationOptions)
