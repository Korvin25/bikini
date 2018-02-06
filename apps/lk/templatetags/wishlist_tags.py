# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def get_product(context, product_id):
    products = context['products']
    return products.get(product_id)


@register.simple_tag(takes_context=True)
def get_product_option(context, option_id):
    product_options = context['product_options']
    return product_options.get(option_id)


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


@register.simple_tag(takes_context=True)
def get_attrs_options(context, items):
    options = {'size': [], 'color': []}
    for slug, option_id in items:
        o = get_option(context, slug, option_id)
        if o:
            attr_type = o.attribute.attr_type
            if attr_type in options.keys():
                options[attr_type].append(o)
    for k, v in options.items():
        options[k] = sorted(v, key=lambda x: x.id)
    return options
