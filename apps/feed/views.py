# -*- coding: utf-8 -*-
from hashlib import md5
from functools import reduce 
import xml.etree.ElementTree as et
from datetime import datetime
from django.http import HttpResponse
from django.template.defaultfilters import striptags
from apps.catalog.models import Product, Category, AttributeOption


SITE_TITLE = u'Интернет магазин мини и микро бикини от Анастасии Ивановской'
SITE_LINK = u'https://bikinimini.ru'
SITE_DESC = u'Большой выбор мини и микро бикини, миниатюрные купальники ручной работы, которые выбирают смелые и уверенные в себе представительницы прекрасного пола.'
SITE_PLATFORM = u'bikinimini'
SITE_COMPANY = u'bikinimini'
SITE_VERSION = u'1.0'
SITE_EMAIL = u'ivan@adving.ru'

HOST = u'https://bikinimini.ru'


class GenerateFeed:
    def __init__(self, name, company, url, platform, version, agency, email):
        self.el_root = et.Element('yml_catalog')
        self.el_root.attrib = {
            'date': datetime.today().isoformat(),
        }
        self.el_shop = self.sub_element(self.el_root, 'shop')
        self.sub_element(self.el_shop, 'name', name)
        self.sub_element(self.el_shop, 'company', company)
        self.sub_element(self.el_shop, 'url', url)
        self.sub_element(self.el_shop, 'platform', platform)
        self.sub_element(self.el_shop, 'version', version)
        self.sub_element(self.el_shop, 'agency', agency)
        self.sub_element(self.el_shop, 'email', email)

        self.currencies = self.sub_element(self.el_shop, 'currencies')
        self.currency = self.sub_element(self.currencies, 'currency')
        self.currency.attrib = {
            'id': 'RUR',
            'rate': '1',
            }

        self.delivery_options = self.sub_element(self.el_shop, 'delivery-options')
        self.option = self.sub_element(self.delivery_options, 'option')
        self.option.attrib = {
            'cost': '400',
            'days': '2',
            }
        
        
        self.categories = self.sub_element(self.el_shop, 'categories')
        for category in Category.objects.filter(is_shown=True):
            self.sub_element(self.categories, 'category', category.title_yandex).attrib = {
                'id': str(category.id),
                }

        self.offers = self.sub_element(self.el_shop, 'offers',)
            
    def sub_element(self, el, name, text=None):
        el = et.SubElement(el, name)
        if text:
            el.text = text
        return el

    def wrap_in_cdata(self, text):
        return u'<![CDATA[ {}]]>'.format(text)

    def create_yandex_item(self, item):
        el_item = self.sub_element(self.offers, 'offer ')
        el_item.attrib = {
            'id': str(item.id)
        }
        hash = md5()
        hash.update(item.get_absolute_url())

        self.sub_element(el_item, 'name', item.title)
        self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
        self.sub_element(el_item, 'vendorCode', item.vendor_code)
        self.sub_element(el_item, 'url', SITE_LINK + item.get_absolute_url())
        self.sub_element(el_item, 'currencyId', 'RUR')
        self.sub_element(el_item, 'price', str(item.price_rub))
        self.sub_element(el_item, 'categoryId', str(item.categories.first().id))
        self.sub_element(el_item, 'description', self.wrap_in_cdata(item.text))
        self.sub_element(el_item, 'country_of_origin', u'Россия')

        self.sub_element(el_item, 'picture', SITE_LINK + item.photo_f.url)
        for photo in item.photos.all()[:9]:
            self.sub_element(el_item, 'picture', SITE_LINK + photo.photo_f.url)

        self.sub_element(el_item, 'param', u'женский' if item.categories.first().sex == 'female' else u'мужской').attrib= {
                u'name': u'Пол',
            }

        for attrs in item.attrs:
            for id in item.attrs[attrs]:
                attr = AttributeOption.objects.get(pk=id)
                if attr.attribute.title not in [u'Низ купальника', u'Верх купальника', u'Фасон', u'Фасон одежды']:
                    if attr.attribute.title == u'Цвет':
                        self.sub_element(el_item, 'param', attr.title).attrib= {
                            u'name': attr.attribute.title,
                        }
                    else:
                        self.sub_element(el_item, 'param', attr.title).attrib= {
                            u'name': attr.attribute.title,
                            u'unit': u'INT'
                        }

        return el_item

    def to_xml(self):
        return et.tostring(self.el_root, encoding="UTF-8")


def yandex_rss(request):
    param = {
        'name': SITE_TITLE,
        'company': SITE_COMPANY,
        'url': SITE_LINK,
        'platform': SITE_PLATFORM,
        'version': SITE_VERSION,
        'agency': SITE_DESC,
        'email': SITE_EMAIL,
    }
    feed = GenerateFeed(**param)

    def html_unescape(text):
        html_escape_table = [
            ['&amp;', "&amp;amp;"],
            ['"', "&amp;quot;"],
            ["'", "&amp;apos;"],
            [">", "&amp;gt;"],
            ["<", "&amp;lt;"],
            [" ", "&amp;nbsp;"],
            ["«", "&amp;laquo;"],
            ["»", "&amp;raquo;"],
            ["–", "&amp;ndash;"],
            ["—", "&amp;mdash;"],
            ["Š", "&amp;Scaron;"],
            ['"', "&quot;"],
            ["'", "&apos;"],
            [">", "&gt;"],
            ["<", "&lt;"],
            [" ", "&nbsp;"],
            ["«", "&laquo;"],
            ["»", "&raquo;"],
            ["–", "&ndash;"],
            ["—", "&mdash;"],
            ["Š", "&Scaron;"],
        ]
        return reduce(lambda text, x: text.replace(x[1], x[0]), html_escape_table, text)

    for product in Product.objects.filter(show=True, show_at_yandex=True):
        feed.create_yandex_item(product)

    return HttpResponse(html_unescape(feed.to_xml()), content_type='text/xml')
