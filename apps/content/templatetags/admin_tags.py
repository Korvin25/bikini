# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.conf import settings

from ..models import Slide

register = template.Library()


@register.filter()
def get_values(form, key):
    return form[key].value()


@register.simple_tag()
def get_slider():
    """
    Кастомный тег для отображения слайдера
    Использование: {% get_slider as slides %}
    """
    return Slide.objects.filter(is_active=True)