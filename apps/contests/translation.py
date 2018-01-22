# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from modeltranslation.translator import register, translator, TranslationOptions

from ..core.translation import MetatagTranslationOptions
from .models import Contest, ContestTitleLine, Participant


@register(Contest)
class ContestTranslationOptions(MetatagTranslationOptions):
    fields = ('title', 'slug', 'terms',)


@register(ContestTitleLine)
class ContestTitleLineTranslationOptions(TranslationOptions):
    fields = ('line',)


@register(Participant)
class ParticipantTranslationOptions(MetatagTranslationOptions):
    fields = ('name', 'description',)
