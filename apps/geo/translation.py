# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import translator

from ..core.translation import TitleTranslationOptions
from .models import Country, City


translator.register(Country, TitleTranslationOptions)
translator.register(City, TitleTranslationOptions)
