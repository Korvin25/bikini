# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.decorators import register
from modeltranslation.translator import translator, TranslationOptions

from ..core.translation import TitleTranslationOptions, MetatagTitleTranslationOptions
from .models import (Attribute, AttributeOption, ExtraProduct, Category,
                     AdditionalProduct, Certificate, Product, ProductOption,)


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'text',
              'meta_title', 'meta_desc', 'meta_keyw', 'seo_text',)


translator.register(Attribute, TitleTranslationOptions)
translator.register(AttributeOption, TitleTranslationOptions)
translator.register(ExtraProduct, TitleTranslationOptions)
translator.register(Category, MetatagTitleTranslationOptions)
translator.register(AdditionalProduct, TitleTranslationOptions)
translator.register(Certificate, TitleTranslationOptions)
translator.register(ProductOption, TitleTranslationOptions)
