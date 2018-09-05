# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.admin.filters import SimpleListFilter
from django.utils.safestring import mark_safe

from ..geo.models import Country


class CountryFilter(SimpleListFilter):
    title = 'Страна'
    parameter_name = 'country'

    def lookups(self, request, model_admin):
        country_ids = set(model_admin.get_queryset(request).values_list('country_id', flat=True))
        countries = Country.objects.filter(id__in=country_ids).values_list('id', 'title')
        return countries

    def queryset(self, request, queryset):
        country_id=self.value()
        if country_id:
            queryset = queryset.filter(id=country_id)
        return queryset


class TrafficSourceFilter(SimpleListFilter):
    title = 'Источник трафика'
    parameter_name = 'traffic_source'

    def lookups(self, request, model_admin):
        LOOKUPS = (
            ('organic', 'Поисковики'),
            ('organic_yandex', 'Поисковики | Яндекс'),
            ('organic_google', 'Поисковики | Google'),
            ('social', 'Соц.сети'),
            ('social_ig', 'Соц.сети | instagram.com'),
            ('social_vk', 'Соц.сети | ВКонтакте'),
            ('social_fb', 'Соц.сети | Facebook'),
            ('social_tw', 'Соц.сети | Twitter'),
            ('ad', 'Реклама'),
            ('ad_yd', mark_safe('Реклама | Яндекс:&nbsp;Директ')),
            ('ad_yno', mark_safe('Реклама | Яндекс:&nbsp;Не&nbsp;определено')),
            ('direct', 'Прямые заходы'),
            ('internal', 'Внутренние переходы'),
            ('referral', 'Переходы с других сайтов'),
            ('none', '-'),
        )
        return LOOKUPS

    def queryset(self, request, queryset):
        FILTERS = {
            'organic': {'ym_source': 'organic'},
            'organic_yandex': {'ym_source': 'organic', 'ym_source_detailed': 'Яндекс'},
            'organic_google': {'ym_source': 'organic', 'ym_source_detailed': 'Google'},
            'social': {'ym_source': 'social'},
            'social_ig': {'ym_source': 'social', 'ym_source_detailed': 'instagram.com'},
            'social_vk': {'ym_source': 'social', 'ym_source_detailed': 'ВКонтакте'},
            'social_fb': {'ym_source': 'social', 'ym_source_detailed': 'Facebook'},
            'social_tw': {'ym_source': 'social', 'ym_source_detailed': 'Twitter'},
            'ad': {'ym_source': 'ad'},
            'ad_yd': {'ym_source': 'ad', 'ym_source_detailed': 'Яндекс: Директ'},
            'ad_yno': {'ym_source': 'ad', 'ym_source_detailed': 'Яндекс: Не определено'},
            'direct': {'ym_source': 'direct'},
            'internal': {'ym_source': 'internal'},
            'referral': {'ym_source': 'referral'},
            'none': {'ym_source': None}
        }
        value = self.value()
        filter = FILTERS.get(value) if value else None
        if filter:
            queryset = queryset.filter(**filter)
        return queryset


def traffic_source_to_str(obj):
    SOURCE_TO_STR = {
        'organic': 'Поисковики',
        'social': 'Соц.сети',
        'ad': 'Реклама',
        'direct': 'Прямой заход',
        'internal': 'Внутренний переход',
        'referral': 'Другой сайт',
        'saved': 'Сохраненная страница',
    }
    ym_source = obj.ym_source
    source_str = SOURCE_TO_STR.get(obj.ym_source, '-')
    return (mark_safe('{} | {}'.format(source_str, obj.ym_source_detailed.replace(' ', '&nbsp;'))) if ym_source in ['organic', 'social', 'ad']
            else source_str)
