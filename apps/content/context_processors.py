# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from ..banners.models import Banner
from .models import Menu


def content(request):
    menu = {m.slug: m.items.all() for m in Menu.objects.prefetch_related('items').all()}
    left_banners = Banner.active_objects.filter(location='left').order_by('?')[:3]
    footer_banner = Banner.active_objects.filter(location='bottom').order_by('?').first()

    content = {
        'menu': menu,
        'left_banners': left_banners,
        'footer_banner': footer_banner,
    }
    return content
