# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django import template
from django.conf import settings


register = template.Library()


# @register.filter
# def attr_in_product(option, product):
#     in_product = bool(product.attrs.get(option.attribute.slug, list()))
#     return in_product


@register.filter
def in_product(option, product):
    in_product = option.id in product.attrs.get(option.attribute.slug, list())
    return in_product


@register.filter
def get_photo_url(option, product):
    slug = option.attribute.slug
    q = {'attrs__{}__contains'.format(slug): option.id}
    photo = product.photos.filter(**q).first()
    # import ipdb; ipdb.set_trace()
    return (photo.style_photo_url if photo
            else option.style_photo_url)


@register.filter
def get_product_url(product, category=None):
    return product.get_absolute_url(category=category)


@register.filter
def get_product_meta_title(product, category=None):
    return product.get_meta_title(category=category)
