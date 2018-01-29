# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_product(context, product_id):
    products = context['products']
    return products[product_id]


@register.simple_tag()
def get_product_url(product, attrs):
    url = product.get_absolute_url()
    if attrs:
        attrs_str = '&'.join(['_{}={}'.format(k, v) for k, v in attrs.items()])
        url = '{}?{}'.format(url, attrs_str)
    return url


@register.simple_tag(takes_context=True)
def get_option(context, slug, option_id):
    options = context['options']
    option = options.get(option_id)
    if option and option.attribute.slug != slug:
        option = None
    return option


@register.filter
def to_json(obj):
    return json.dumps(obj)
