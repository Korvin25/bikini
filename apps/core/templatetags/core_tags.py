# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
from itertools import chain

from django import template
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils import translation

from crequest.middleware import CrequestMiddleware


register = template.Library()

DEFAULT_SITENAME = settings.DEFAULT_SITENAME


@register.filter
def add_subdomain(url):
    """
    Меняем основной домен на субдомен, если:
        - основной домен найден в урле
        - мы находимся на субдомене
    (используется для разных баннерах, урлы для которых задаются в админке)
    """
    request = CrequestMiddleware.get_request()
    default_url = '{}://{}'.format(request.scheme, DEFAULT_SITENAME)

    if url.startswith(default_url) and request.region_code:
        url = url.replace(DEFAULT_SITENAME, request.get_host(), 1)
    return url


@register.filter
def full_url(url):
    """
    Получаем полный URL текущей страницы, включая домен и языковые префиксы
    (используется для расшаривания в соц.сетях)
    """
    request = CrequestMiddleware.get_request()
    current_site = get_current_site(request)
    return '{}://{}{}'.format(request.scheme, current_site.domain, url)


@register.simple_tag(takes_context=True)
def get_current_path(context):
    """
    Получаем абсолютный путь текущей страницы без языковых префиксов
    (используется для переключения языков в шапке)
    """
    path = context['request'].path
    languages = settings.LANGUAGES_DICT.keys()
    for lang in languages:
        _lang = '/{}/'.format(lang)
        if path.startswith(_lang):
            path = path.replace(_lang, '/', 1)
            break
    return path


@register.simple_tag(takes_context=True)
def get_translated_path(context, lang=None):
    path = context['request'].path
    obj = (context.get('product')
           or context.get('category')
           or context.get('video')
           or context.get('post')
           or context.get('participant')
           or context.get('contest'))
    if obj and lang:
        current_language = translation.get_language()
        translation.activate(lang)
        path = obj.get_absolute_url()
        translation.activate(current_language)
    else:
        path = get_current_path(context)
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
    return 'http://{}{}'.format(current_site.domain, url)


@register.assignment_tag()
def is_divisible(number1, number2):
    """
    Определяем, делится ли первое число на второе
    """
    return not (number1 % number2)


@register.filter
def to_str(something):
    """
    Переводим что-либо в строку
    (используется для Decimal, которые должны быть представлены в виде "123.00", а не "123,00")
    """
    return unicode(something)


@register.filter
def to_phone(phone_number):
    phone = ''.join([s for s in phone_number if s in '+1234567890'])
    return phone


@register.filter
def to_viber(phone_number):
    phone = ''.join([s for s in phone_number if s in '+1234567890'])
    if phone[0] == '+':
        phone = phone[1:]
    if phone.startswith('7'):
        phone = phone[1:]
    #phone = '+38{}'.format(phone)
    return phone


@register.filter
def to_telegram(telegram_login):
    telegram_login = (telegram_login or '').replace('@', '').replace(' ', '')
    return telegram_login


@register.filter
def get_value(dict_value, key):
    return dict_value.get(key)


@register.filter
def to_int(value):
    return int(value)


@register.filter
def to_int_str(value):
    value = int(value) if int(value) == value else value
    return str(value)


@register.filter
def to_price(value):
    if type(value) not in [int, float, Decimal]:
        return unicode(value)

    int_value = int(value)
    return (int_value if int_value == value
            else '{:.2f}'.format(value))


@register.filter
def with_delimeter(value):
    return '{0:,}'.format(value).replace(',', ' ')


@register.filter
def to_int_plus(value):
    int_value = int(value)
    return int_value if int_value == value else int_value + 1


@register.filter
def to_int_or_float(value):
    int_value = int(value)
    return int_value if int_value == value else float(value)


@register.filter
def with_discount(price, discount):
    discount_price = price*discount // 100
    # return to_int_plus(price - discount_price)
    return to_int_or_float(price - discount_price)


@register.filter
def with_br(title):
    return title.replace(' ', '<br>')
