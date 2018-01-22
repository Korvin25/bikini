# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from ..banners.models import Banner
from .models import Menu


def content(request):
    menu = {m.slug: m.items.all() for m in Menu.objects.prefetch_related('items').all()}
    left_banners = Banner.active_objects.filter(location='left').order_by('?')[:3]
    footer_banner = Banner.active_objects.filter(location='bottom').order_by('?').first()
    LANGUAGES = settings.LANGUAGES
    LANGUAGES_DICT = settings.LANGUAGES_DICT
    liked_participants = request.session.get('liked_participants', [])

    content = {
        'menu': menu,
        'left_banners': left_banners,
        'footer_banner': footer_banner,
        'LANGUAGES': LANGUAGES,
        'LANGUAGES_DICT': LANGUAGES_DICT,
        'liked_participants': liked_participants,
    }
    return content
