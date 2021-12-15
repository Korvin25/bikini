# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, TranslationOptions

from .models import DeliveryMethod, PaymentMethod


@register(DeliveryMethod)
class DeliveryMethodTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(PaymentMethod)
class PaymentMethodTranslationOptions(TranslationOptions):
    fields = ('title',)
