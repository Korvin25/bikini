# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from .models import Menu


def content(request):
    menu = {m.slug: m.items.all() for m in Menu.objects.prefetch_related('items').all()}

    content = {
        'menu': menu,
    }
    return content
