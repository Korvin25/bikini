# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class RedirectToMainDomain(BaseException):
    pass


SEO_SUFFIXES = {
    'spb': 'в Санкт-Петербурге',
    'nsk': 'в Новосибирске',
    'sam': 'в Самаре',
    'sch': 'в Сочи',
    'smf': 'в Симферополе',
    'svs': 'в Севастополе',
    None: '',
}

class CurrentSiteAndRegionMiddleware(MiddlewareMixin):

    def process_request(self, request):
        domain = request.get_host()
        try:
            site = Site.objects.get(domain=domain)

            region_code = domain.split('.')[0] if (site.id > 1) else None
            request.region_code = {
                'spb': 'spb',
                'nsk': 'nsk',
                'sam': 'sam',
                'sochi': 'sch',
                'simferopol': 'smf',
                'sevastopol': 'svs',
            }.get(region_code, region_code)
            request.region_seo_suffix = SEO_SUFFIXES.get(request.region_code, '')

            if request.region_code:
                lang_prefix = request.path[1:].split('/')[0]
                if lang_prefix.lower() in settings.LANGUAGES_DICT.keys():
                    raise RedirectToMainDomain

        except (Site.DoesNotExist, RedirectToMainDomain) as e:
            # определение по ip?
            domain = Site.objects.order_by('id').first().domain
            return HttpResponseRedirect('{}://{}{}'.format(request.scheme, domain, request.get_full_path()))

        return None
