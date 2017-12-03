# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# from jet.admin import CompactInline
from modeltranslation.admin import TranslationInlineModelAdmin, TabbedTranslationAdmin
# from tabbed_admin import TabbedModelAdmin

from .models import Country, City
from .translation import *


class CityInline(TranslationInlineModelAdmin, admin.StackedInline):  # CompactInline
    model = City
    fields = ('title', 'order',)
    suit_classes = 'suit-tab suit-tab-cities'
    extra = 0
    show_change_link = True


@admin.register(Country)
class CountryAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'order',)
    list_editable = ('order',)
    inlines = [CityInline, ]
    suit_form_tabs = (('default', 'Общее'), ('cities', 'Города'),)
    fieldsets = (
        ('Общее', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('id', 'title', 'order',)
        }),
    )
    readonly_fields = ('id',)


@admin.register(City)
class CityAdmin(TabbedTranslationAdmin):
    list_display = ('title_ru', 'country', 'order',)
    list_filter = ('country',)
    list_editable = ('order',)
    list_per_page = 200
