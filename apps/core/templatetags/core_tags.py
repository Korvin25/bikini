# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django import template
from django.contrib.sites.shortcuts import get_current_site


register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_path(context):
    """
    Получаем абсолютный путь текущей страницы без языковых префиксов
    (используется для переключения языков в шапке)
    """
    path = context['request'].path
    path = (path.replace('/ru/', '/', 1) if path.startswith('/ru/')
            else path.replace('/en/', '/', 1) if path.startswith('/en/')
            else path)
    return path


@register.assignment_tag(takes_context=True)
def get_current_slug(context):
    """
    Получаем slug текущей страницы
    (костыль для подсветки активного пункта меню)
    """
    path = get_current_path(context)
    slug = path.split('/')[1]
    return slug


@register.assignment_tag(takes_context=True)
def get_profile_slug(context):
    """
    Получаем slug текущей страницы
    (для меню пользователя)
    """
    path = get_current_path(context)
    slug = path.split('/')[2]
    return slug


@register.assignment_tag(takes_context=True)
def get_full_url(context, url, request=None):
    """
    Получаем полный URL текущей страницы, включая домен и языковые префиксы
    (используется для расшаривания в соц.сетях)
    """
    if request is None:
        request = context['request']
    current_site = get_current_site(request)
    return 'http://{0}{1}'.format(current_site.domain, url)


@register.assignment_tag()
def is_divisible(number1, number2):
    """
    Определяем, делится ли первое число на второе
    """
    return not (number1 % number2)


@register.simple_tag()
def to_str(something):
    """
    Переводим что-либо в строку
    (используется для Decimal, которые должны быть представлены в виде "123.00", а не "123,00")
    """
    return str(something)


@register.filter
def to_phone(phone_number):
    phone = ''.join([s for s in phone_number if s in '+1234567890'])
    return phone
