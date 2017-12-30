# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import Country


def populate_countries():
    countries = []

    with open('apps/geo/countries.txt') as countries_file:
        countries = countries_file.read().decode('utf-8').split('\n')

    for i, title in enumerate(countries):
        country, _created = Country.objects.get_or_create(id=(i+1), defaults={'title': title})
        if _created is False:
            country.title = title
            country.save()
        print country.id, country.title
