# -*- coding: utf-8 -*-
import xml.etree.ElementTree as et
from datetime import datetime
from functools import reduce

from apps.catalog.models import AttributeOption, Category


class GenerateFeed:
    def __init__(self, name, company, url, platform, version, agency, email, weight, dimensions):
        self.weight, self.dimensions, self.site_link = weight, dimensions, url
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

        self.sub_element(el_item, 'name', item.title)
        self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
        self.sub_element(el_item, 'vendorCode', item.vendor_code)
        self.sub_element(el_item, 'url', self.site_link + item.get_absolute_url())
        self.sub_element(el_item, 'currencyId', 'RUR')
        self.sub_element(el_item, 'price', str(item.price_rub))
        self.sub_element(el_item, 'categoryId', str(item.categories.first().id))
        self.sub_element(el_item, 'description', self.wrap_in_cdata(item.text))
        self.sub_element(el_item, 'country_of_origin', u'Россия')
        self.sub_element(el_item, 'weight', self.weight)
        self.sub_element(el_item, 'dimensions', self.dimensions)

        self.sub_element(el_item, 'picture', self.site_link + item.photo_f.url)
        for photo in item.photos.all()[:9]:
            self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

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

    def create_aliexpress_item(self, item):
        i=0
        el_item = self.sub_element(self.offers, 'offer ')
        el_item.attrib = {
            'id': '1000'+str(item.id) + str(i),
            'group_id': '10'+str(item.id)
        }
        name = item.title + u' от Анастасии Ивановской'
        dimensions = self.dimensions.split('/')

        self.sub_element(el_item, 'name', name)
        self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
        self.sub_element(el_item, 'sku_code', item.vendor_code + str(i))
        self.sub_element(el_item, 'url', self.site_link + item.get_absolute_url())
        self.sub_element(el_item, 'currencyId', 'RUR')
        self.sub_element(el_item, 'price', str(item.price_rub))
        self.sub_element(el_item, 'categoryId', str(item.categories.first().id))
        self.sub_element(el_item, 'description', self.wrap_in_cdata(item.text))
        self.sub_element(el_item, 'country_of_origin', u'Россия')
        self.sub_element(el_item, 'weight', self.weight)
        self.sub_element(el_item, 'length', dimensions[0])
        self.sub_element(el_item, 'width', dimensions[1])
        self.sub_element(el_item, 'height', dimensions[2])
        self.sub_element(el_item, 'quantity', str(item.in_stock_counts['in_stock__min']))

        self.sub_element(el_item, 'picture', self.site_link + item.photo_f.url)
        for photo in item.photos.all()[:5]:
            self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

        colors = item.attrs.get('color', False)
        if colors:
            attr = AttributeOption.objects.get(pk=colors[-1])

            if attr.picture:
                self.sub_element(el_item, 'sku_picture', self.site_link + self.site_link + attr.picture.url)

            self.sub_element(el_item, 'cus_skucolor', attr.title)
            colors.pop()

            for id in colors:
                attr = AttributeOption.objects.get(pk=id)
                url_color_image = None
                if attr.picture:
                    url_color_image = attr.picture.url
                i+=1
                self.create_aliexpress_params(item, attr.title, i, chech_color=True, url_color_image=url_color_image)
    
        return el_item

    def create_aliexpress_params(self, item, param, i=0, chech_color=False, url_color_image=None):
        el_item = self.sub_element(self.offers, 'offer ')
        el_item.attrib = {
            'id': '1000'+str(item.id) + str(i),
            'group_id': '10'+str(item.id)
        }
        name = item.title + u' от Анастасии Ивановской'
        dimensions = self.dimensions.split('/')

        self.sub_element(el_item, 'name', name)
        self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
        self.sub_element(el_item, 'sku_code', item.vendor_code + str(i))
        self.sub_element(el_item, 'url', self.site_link + item.get_absolute_url())
        self.sub_element(el_item, 'currencyId', 'RUR')
        self.sub_element(el_item, 'price', str(item.price_rub))
        self.sub_element(el_item, 'categoryId', str(item.categories.first().id))
        self.sub_element(el_item, 'description', self.wrap_in_cdata(item.text))
        self.sub_element(el_item, 'country_of_origin', u'Россия')
        self.sub_element(el_item, 'weight', self.weight)
        self.sub_element(el_item, 'length', dimensions[0])
        self.sub_element(el_item, 'width', dimensions[1])
        self.sub_element(el_item, 'height', dimensions[2])
        self.sub_element(el_item, 'quantity', str(item.in_stock_counts['in_stock__min']))

        self.sub_element(el_item, 'picture', self.site_link + item.photo_f.url)
        for photo in item.photos.all()[:9]:
            self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

        if chech_color:
            self.sub_element(el_item, 'cus_skucolor', param)
        if url_color_image:
                self.sub_element(el_item, 'sku_picture', self.site_link + self.site_link + url_color_image)
        
        # for attrs in item.attrs:
        #     for id in item.attrs[attrs]:
        #         attr = AttributeOption.objects.get(pk=id)
        #         if attr.attribute.title not in [u'Низ купальника', u'Верх купальника', u'Фасон', u'Фасон одежды']:
        #             if attr.attribute.title == u'Размер низ':
        #                 i+=1
        #                 self.create_aliexpress_params(item, attr.title, i, chech_color=True)



    def to_xml(self):
        return et.tostring(self.el_root, encoding="UTF-8")


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
