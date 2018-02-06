# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from django import template
from django.conf import settings

from apps.catalog.models import AttributeOption, ExtraProduct, Category


register = template.Library()


@register.filter
def get_product_url(product, category_or_sex=None):
    category = sex = None
    if isinstance(category_or_sex, Category):
        category = category_or_sex
    else:
        sex = category_or_sex
    return product.get_absolute_url(category=category, sex=sex)


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
def get_product_meta_title(product, category=None):
    return product.get_meta_title(category=category)


@register.filter
def had_neighbor(attr, attr_ids):
    neighbors_ids = attr['attr'].from_neighbor.all().values_list('id', flat=True)
    return True if (set(neighbors_ids) & set(attr_ids)) else False


@register.simple_tag
def item_extra_products_str(item):
    pieces = []
    extra_products_ids = item.extra_products.keys()
    pieces = ['+ {}'.format(extra_p.title) for extra_p in ExtraProduct.objects.filter(id__in=extra_products_ids)]
    return '<br/>'.join(pieces)


@register.simple_tag
def item_color(item, color_attribute):
    option = None
    color_option_id = item.attrs.get('color')

    if color_option_id:
        try:
            option = AttributeOption.objects.get(attribute_id=color_attribute.id, id=color_option_id)
        except AttributeOption.DoesNotExist:
            pass

    return option


@register.simple_tag(takes_context=True)
def get_is_chosen(context, attr_slug, option_id):
    chosen_options = context.get('chosen_options', {})
    chosen_id = chosen_options.get(attr_slug, '')
    return unicode(option_id) == unicode(chosen_id)


@register.simple_tag()
def get_product_text(product):
    # return product.seo_text or product.text
    return product.get_text()


@register.simple_tag()
def get_product_attrs_url(product, attrs, extra_products=None, wrapping_price=None):
    extra_products = extra_products or {}
    with_wrapping = bool(wrapping_price)
    url = product.get_absolute_url()

    attrs_strings = []
    for k, v in attrs.iteritems():
        attrs_strings.append('_{}={}'.format(k, v))
    for k, d in extra_products.iteritems():
        for slug, id in d.iteritems():
            attrs_strings.append('_{}_{}={}'.format(k, slug, id))
    if with_wrapping:
        attrs_strings.append('_with_wrapping=1')

    if len(attrs_strings):
        attrs_str = '&'.join(attrs_strings)
        url = '{}?{}'.format(url, attrs_str)
    return url
