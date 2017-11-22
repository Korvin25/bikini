# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, translator, TranslationOptions

from ..core.translation import TitleTranslationOptions, MetatagTitleTranslationOptions
from .models import (Attribute, AttributeOption, ExtraProduct, Category,
                     AdditionalProduct, Certificate, Product, ProductOption,)


@register(Product)
class ProductTranslationOptions(MetatagTitleTranslationOptions):
    fields = ('subtitle', 'text', 'slug',)
    # empty_values = {'slug': None}


@register(Category)
class CategoryTranslationOptions(MetatagTitleTranslationOptions):
    fields = ('slug',)
    # empty_values = {'slug': None}


translator.register(Attribute, TitleTranslationOptions)
translator.register(AttributeOption, TitleTranslationOptions)
translator.register(ExtraProduct, TitleTranslationOptions)
translator.register(AdditionalProduct, TitleTranslationOptions)
translator.register(Certificate, TitleTranslationOptions)
translator.register(ProductOption, TitleTranslationOptions)
