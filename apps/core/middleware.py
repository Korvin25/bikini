# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class RedirectToMainDomain(BaseException):
    pass


class CurrentSiteAndRegionMiddleware(MiddlewareMixin):

    def process_request(self, request):
        domain = request.get_host()
        try:
            site = Site.objects.get(domain=domain)
            request.region_code = domain.split('.')[0] if (site.id > 1) else None

            if request.region_code:
                lang_prefix = request.path[1:].split('/')[0]
                if lang_prefix.lower() in settings.LANGUAGES_DICT.keys():
                    raise RedirectToMainDomain

        except (Site.DoesNotExist, RedirectToMainDomain) as e:
            # определение по ip?
            domain = Site.objects.order_by('id').first().domain
            return HttpResponseRedirect('{}://{}{}'.format(request.scheme, domain, request.get_full_path()))

        return None
