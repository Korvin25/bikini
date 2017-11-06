# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from jet.admin import CompactInline
from modeltranslation.admin import TranslationTabularInline, TabbedTranslationAdmin

from .models import Country, City
from .translation import *


# class CityInline(TranslationTabularInline):
# class CityInline(admin.TabularInline):
class CityInline(CompactInline):
    model = City
    fields = ('title_ru', 'title_en', 'title_de', 'title_fr', 'title_it', 'title_es', 'order',)
    extra = 0
    show_change_link = True


@admin.register(Country)
class CountryAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'order',)
    list_editable = ('order',)
    inlines = [CityInline, ]


@admin.register(City)
class CityAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'country', 'order',)
    list_filter = ('country',)
    list_editable = ('order',)
    list_per_page = 200
