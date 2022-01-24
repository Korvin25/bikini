# -*- coding: utf-8 -*-
from unicodedata import category
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

    def create_ozon_item(self, item):
        colors_id = item.attrs.get('color', [])
        sizes_id = item.attrs.get('bottom_size', []) + item.attrs.get('top_size', [])  + item.attrs.get('size', []) + item.attrs.get('razmer_kupalnika', []) + item.attrs.get('size_yubka_dop', [])
        shueze_size_id =  item.attrs.get('shueze_size', []) 
        colors = AttributeOption.objects.filter(pk__in=colors_id)
        sizes = [s.title for s in AttributeOption.objects.filter(pk__in=sizes_id)]
        shueze_sizes = [sh.title for sh in AttributeOption.objects.filter(pk__in=shueze_size_id)]
        sizes = list(set(sizes))
        price = str(item.price_rub)
        item_id = str(item.id)
        instock = str(item.in_stock_counts['in_stock__min'])

        i=0

        for color in colors:
            if not sizes and not shueze_sizes: # если нет размера, в основносм это аксесуары
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + '_' + str(i),
                }
                self.sub_element(el_item, 'price', price)
                # self.sub_element(el_item, 'oldprice', price)
                # self.sub_element(el_item, 'premium_price', price)
                outlets = self.sub_element(el_item, 'outlets')
                self.sub_element(outlets, 'outlet').attrib = {
                    'instock': instock,
                }

            for size in sizes:
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + '_' + str(i),
                }
  
                self.sub_element(el_item, 'price', price)
                # self.sub_element(el_item, 'oldprice', price)
                # self.sub_element(el_item, 'premium_price', price)
                outlets = self.sub_element(el_item, 'outlets')
                self.sub_element(outlets, 'outlet').attrib = {
                    'instock': instock,
                }

            for shueze_size in shueze_sizes: # обувь
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + '_' + str(i),
                }
                self.sub_element(el_item, 'price', price)
                # self.sub_element(el_item, 'oldprice', price)
                # self.sub_element(el_item, 'premium_price', price)
                outlets = self.sub_element(el_item, 'outlets')
                self.sub_element(outlets, 'outlet').attrib = {
                    'instock': instock,
                }

    def create_yandex_item(self, item):
        letters = 'A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z,AA,AB,AC,AD,AE,AF,AG,AH,AI,AJ,AK,AL,AM,AN,AO,AP,AQ,AR,AS,AT,AU,AV,AW,AX,AY,AZ'.split(',')
        name = item.title + u' от Анастасии Ивановской'
        colors_id = item.attrs.get('color', [])
        sizes_id = item.attrs.get('bottom_size', []) + item.attrs.get('top_size', [])  + item.attrs.get('size', []) + item.attrs.get('razmer_kupalnika', []) + item.attrs.get('size_yubka_dop', [])
        shueze_size_id =  item.attrs.get('shueze_size', []) 
        colors = [c.title for c in AttributeOption.objects.filter(pk__in=colors_id)]
        sizes = [s.title for s in AttributeOption.objects.filter(pk__in=sizes_id)]
        shueze_sizes = [sh.title for sh in AttributeOption.objects.filter(pk__in=shueze_size_id)]
        sizes = list(set(sizes))
        price = str(item.price_rub)
        item_id = str(item.id)
        famile = u'женский' if item.categories.first().sex == 'female' else u'мужской'
        photos = item.photos.all()[:9]
        picture = self.site_link + item.photo_f.url
        text = self.wrap_in_cdata(item.text) 
        categorys_product = item.categories.all()
        categorys_product = categorys_product.exclude(title=u"Happy new year")
        categoryId = str(categorys_product[0].id)
        url = self.site_link + item.get_absolute_url()
        vendorCode = item.vendor_code
        name = item.title
        i=0

        for color in colors:
            if not sizes and not shueze_sizes: # если нет размера, в основносм это аксесуары
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + letters[i-1],
                    'group_id': item_id
                }

                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'vendorCode', vendorCode)
                self.sub_element(el_item, 'url', url)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', text)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'dimensions', self.dimensions)

                self.sub_element(el_item, 'picture', picture)
                for photo in photos:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

                self.sub_element(el_item, 'param', famile).attrib= {
                        u'name': u'Пол',
                    }

                self.sub_element(el_item, 'param', color).attrib= {
                        u'name': u'Цвет',
                    }

            for size in sizes:
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + letters[i-1],
                    'group_id': item_id
                }

                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'vendorCode', vendorCode)
                self.sub_element(el_item, 'url', url)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', text)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'dimensions', self.dimensions)

                self.sub_element(el_item, 'picture', picture)
                for photo in photos:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

                self.sub_element(el_item, 'param', famile).attrib= {
                        u'name': u'Пол',
                    }

                self.sub_element(el_item, 'param', color).attrib= {
                        u'name': u'Цвет',
                    }
                self.sub_element(el_item, 'param', size).attrib= {
                        u'name': u'Размер',
                        u'unit': u'INT'
                    }

            for shueze_size in shueze_sizes: # обувь
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': item_id + letters[i-1],
                    'group_id': item_id
                }

                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'vendorCode', vendorCode)
                self.sub_element(el_item, 'url', url)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', text)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'dimensions', self.dimensions)

                self.sub_element(el_item, 'picture', picture)
                for photo in photos:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

                self.sub_element(el_item, 'param', famile).attrib= {
                        u'name': u'Пол',
                    }

                self.sub_element(el_item, 'param', color).attrib= {
                        u'name': u'Цвет',
                    }
                self.sub_element(el_item, 'param', shueze_size).attrib= {
                        u'name': u'Размер',
                        u'unit': u'RU'
                    }

    def create_aliexpress_item(self, item):
        i=0
        dimensions = self.dimensions.split('/')
        name = item.title + u' от Анастасии Ивановской'
        colors_id = item.attrs.get('color', [])
        sizes_id = item.attrs.get('bottom_size', []) + item.attrs.get('top_size', [])  + item.attrs.get('size', []) + item.attrs.get('razmer_kupalnika', []) + item.attrs.get('size_yubka_dop', [])
        shueze_size_id =  item.attrs.get('shueze_size', []) 
        colors = AttributeOption.objects.filter(pk__in=colors_id)
        sizes = [s.title for s in AttributeOption.objects.filter(pk__in=sizes_id)]
        shueze_sizes = [sh.title for sh in AttributeOption.objects.filter(pk__in=shueze_size_id)]
        sizes = list(set(sizes))

        photos_html = """
            <p>
                <img src="{}">
            </p>
        """
        site_link = self.site_link + item.get_absolute_url()
        vendor_code = item.vendor_code
        categorys_product = item.categories.all()
        categorys_product = categorys_product.exclude(title=u"Happy new year")
        categoryId = str(categorys_product[0].id)
        price = str(item.price_rub)
        photos = item.photos.all()
        photo_first = self.site_link + item.photo_f.url
        text = item.text or ''

        text += u'<p>Если хотите разный размер верха и низа, то пишите комментарий к заказу</p>'

        if photo_first:
            text += photos_html.format(photo_first)

        for photo in photos:
            text += photos_html.format(self.site_link + photo.photo_f.url)

        description = self.wrap_in_cdata(text)
        item_id = str(item.id)

        quantity = str(item.in_stock_counts['in_stock__min'])

        for color in colors:
            if not sizes and not shueze_sizes: # если нет размера, в основносм это аксесуары
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': '1000'+item_id + str(i),
                    'group_id': '10'+item_id
                }
                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'sku_code', vendor_code + str(i))
                self.sub_element(el_item, 'url', site_link)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', description)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'length', dimensions[0])
                self.sub_element(el_item, 'width', dimensions[1])
                self.sub_element(el_item, 'height', dimensions[2])
                self.sub_element(el_item, 'quantity', quantity)
                self.sub_element(el_item, 'cus_skucolor', color.title)
                self.sub_element(el_item, 'param', color.title).attrib = {
                    "name" : "cus_skucolor"
                }
                if color.picture:
                    self.sub_element(el_item, 'sku_picture', self.site_link + color.picture.url)
                    self.sub_element(el_item, 'param', self.site_link + color.picture.url).attrib = {
                    "name" : "sku_picture"
                }
                if photo_first:
                    self.sub_element(el_item, 'picture', photo_first)
                for photo in photos[:5]:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

            for size in sizes:
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': '1000'+item_id + str(i),
                    'group_id': '10'+item_id
                }
  
                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'sku_code', vendor_code + str(i))
                self.sub_element(el_item, 'url', site_link)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', description)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'length', dimensions[0])
                self.sub_element(el_item, 'width', dimensions[1])
                self.sub_element(el_item, 'height', dimensions[2])
                self.sub_element(el_item, 'quantity', quantity)
                self.sub_element(el_item, 'size', size)
                self.sub_element(el_item, 'cus_skucolor', color.title)
                self.sub_element(el_item, 'param', color.title).attrib = {
                    "name" : "cus_skucolor"
                }
                if color.picture:
                    self.sub_element(el_item, 'sku_picture', self.site_link + color.picture.url)
                    self.sub_element(el_item, 'param', self.site_link + color.picture.url).attrib = {
                    "name" : "sku_picture"
                }
                if photo_first:
                    self.sub_element(el_item, 'picture', photo_first)
                for photo in photos[:5]:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

            for shueze_size in shueze_sizes: # обувь
                i += 1
                el_item = self.sub_element(self.offers, 'offer ')
                el_item.attrib = {
                    'id': '1000'+item_id + str(i),
                    'group_id': '10'+item_id
                }
  
                self.sub_element(el_item, 'name', name)
                self.sub_element(el_item, 'vendor', 'Anastasiya Ivanovskaya')
                self.sub_element(el_item, 'sku_code', vendor_code + str(i))
                self.sub_element(el_item, 'url', site_link)
                self.sub_element(el_item, 'currencyId', 'RUR')
                self.sub_element(el_item, 'price', price)
                self.sub_element(el_item, 'categoryId', categoryId)
                self.sub_element(el_item, 'description', description)
                self.sub_element(el_item, 'country_of_origin', u'Россия')
                self.sub_element(el_item, 'weight', self.weight)
                self.sub_element(el_item, 'length', dimensions[0])
                self.sub_element(el_item, 'width', dimensions[1])
                self.sub_element(el_item, 'height', dimensions[2])
                self.sub_element(el_item, 'quantity', quantity)
                self.sub_element(el_item, 'size', shueze_size)
                self.sub_element(el_item, 'cus_skucolor', color.title)
                self.sub_element(el_item, 'param', color.title).attrib = {
                    "name" : "cus_skucolor"
                }
                if color.picture:
                    self.sub_element(el_item, 'sku_picture', self.site_link + color.picture.url)
                    self.sub_element(el_item, 'param', self.site_link + color.picture.url).attrib = {
                    "name" : "sku_picture"
                }
                if photo_first:
                    self.sub_element(el_item, 'picture', photo_first)
                for photo in photos[:5]:
                    self.sub_element(el_item, 'picture', self.site_link + photo.photo_f.url)

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
