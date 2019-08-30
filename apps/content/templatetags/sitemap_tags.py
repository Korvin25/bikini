# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.contrib.sites.shortcuts import get_current_site

from crequest.middleware import CrequestMiddleware


register = template.Library()


@register.filter()
def update_host(url):
    request = CrequestMiddleware.get_request()
    host = request.get_host()
    default_host = get_current_site(request).domain
    if host != default_host:
        url = url.replace(default_host, host, 1)
    return url
