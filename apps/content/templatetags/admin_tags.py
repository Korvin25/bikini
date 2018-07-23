# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template


register = template.Library()


@register.filter()
def get_values(form, key):
    return form[key].value()
