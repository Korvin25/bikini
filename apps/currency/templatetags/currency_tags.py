# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.simple_tag
def prefix_currency(currency, value=''):
    pure_value = unicode(value)
    empty_char = ' ' if (' ' in pure_value) else ''

    if currency == 'eur':
        return mark_safe('<span title="eur">€</span>{}'.format(empty_char))
    elif currency == 'usd':
        return mark_safe('<span title="usd">$</span>{}'.format(empty_char))
    return ''


@register.simple_tag
def postfix_currency(currency, value=''):
    if currency == 'rub':
        pure_value = unicode(value)
        empty_char = ' ' if (' ' in pure_value) else ''

        return mark_safe('{}<abbr title="руб">р.</abbr>'.format(empty_char))
    return ''


@register.filter
def with_currency(value, currency, pure_value=None, full=False, with_dot=True, light=False,
                  with_title=True, without_space=False):
    pure_value = unicode(pure_value or value)
    empty_char = ' ' if (' ' in pure_value) else ''

    if currency == 'rub':
        rub = 'руб' if full else 'р'
        rub = '{}.'.format(rub) if with_dot else rub
        title = ' title="руб"' if with_title else ''
        value = ('{}{}<abbr{}>{}</abbr>'.format(value, empty_char, title, rub) if not light
                 else '{} {}'.format(value, rub) if not without_space
                 else '{}{}'.format(value, rub))
    elif currency == 'eur':
        title = ' title="eur"' if with_title else ''
        value = ('<span{}>€</span>{}{}'.format(title, empty_char, value) if not light
                 else '€ {}'.format(value) if not without_space
                 else '€{}'.format(value))
    elif currency == 'usd':
        title = ' title="usd"' if with_title else ''
        value = ('<span{}>$</span>{}{}'.format(title, empty_char, value) if not light
                 else '$ {}'.format(value) if not without_space
                 else '${}'.format(value))
    return value


@register.filter
def currency_light(value, currency):
    return with_currency(value, currency, light=True)


@register.filter
def currency_light_without_dot(value, currency):
    return with_currency(value, currency, light=True, with_dot=False, without_space=True)


@register.filter
def currency_compact(value, currency):
    return with_currency(value, currency, light=True, without_space=True)


@register.filter
def currency_simple(value, currency):
    return with_currency(value, currency, with_title=False)


@register.filter
def with_js_cart_summary(value, currency):
    html_value = '<span class="js-cart-summary">{}</span>'.format(value)
    return with_currency(html_value, currency, pure_value=value)


@register.filter
def with_js_certificte_price(value, currency):
    html_value = '<span class="js-certificte-price">{}</span>'.format(value)
    return with_currency(html_value, currency, pure_value=value, full=True)
