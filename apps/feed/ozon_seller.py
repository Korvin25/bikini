# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import json  

from django.utils.html import strip_tags
from django.conf import settings

from apps.feed.mapping import COLORS_MAP, SIZES_FAMELE_MAP, SIZES_MEN_MAP
from apps.catalog.models import AttributeOption


class OzonSeller():
    '''Класс для работы с озон api(в для загрузки обновления продуктов).
    '''
    
    def __init__(self, api_key, client_id):
        self.site_link = settings.SITE_LINK
        self.api_key = api_key
        self.client_id = client_id
        self. headers = {
            'Host': 'api-seller.ozon.ru',
            'Client-Id': '283157',
            'Api-Key': '613c58bf-b1d5-4573-84b2-9c463055bcfb',
            'Content-Type': 'application/json',
        }
        self.url = 'https://api-seller.ozon.ru/v2/product/import'

    @staticmethod
    def get_attributes(id, value):
        obj = {"id": id,"values": [{"value": value }]}
        return obj

    def update_product(self, product):
        try:
            lists = {
                "items": []
            }

            colors_id = product.attrs.get('color', [])
            sizes_id = product.attrs.get('bottom_size', []) + product.attrs.get('top_size', [])  + product.attrs.get('size', []) + product.attrs.get('razmer_kupalnika', []) + product.attrs.get('size_yubka_dop', [])
            shueze_size_id =  product.attrs.get('size_yubka_dop', []) 
            colors = [c.title for c in AttributeOption.objects.filter(pk__in=colors_id)]
            sizes = [s.title for s in AttributeOption.objects.filter(pk__in=sizes_id)]
            shueze_sizes = [sh.title for sh in AttributeOption.objects.filter(pk__in=shueze_size_id)]
            sizes = list(set(sizes))

            name = product.title + u' от Анастасии Ивановской'
            categorys_product = product.categories.all()
            categorys_product = categorys_product.exclude(title=u"Happy new year")
            category_id = categorys_product[0].ozon_category_id
            offer_id = str(product.id)
            primary_image = self.site_link + product.photo_f.url
            images = [self.site_link + photo.photo_f.url for photo in product.photos.all()[:13]]
            price = price = str(product.price_rub)
            vendor_code = str(product.vendor_code)
            mod = product.title
            text = strip_tags(product.text)
            attributes_type = categorys_product[0].title
            i = 0

            print(sizes)
            print(colors)
            print(shueze_sizes)

            for color in colors:
                if not sizes: # если нет размера, в основносм это аксесуары
                    i += 1
                    param_dict = {
                        "attributes": [],
                        "barcode": "",
                        "category_id": category_id,
                        "color_image": "",
                        "complex_attributes": [ ],
                        "depth": 30,
                        "dimension_unit": "mm",
                        "height": 300,
                        "images": images,
                        "images360": [ ],
                        "name": name,
                        "offer_id": offer_id + '_' + str(i),
                        "old_price": "",
                        "pdf_list": [ ],
                        "premium_price": "",
                        "price": price,
                        "primary_image": primary_image,
                        "vat": "0.1",
                        "weight": 100,
                        "weight_unit": "g",
                        "width": 250
                    }
                
                    sex = u'Женский' if categorys_product[0].sex == 'female' else u'Мужской'

                    param_dict['attributes'].append(self.get_attributes(8292, vendor_code)) #обьеденить на одной карточке
                    for color in COLORS_MAP[color]:
                        param_dict['attributes'].append(self.get_attributes(10096, color)) # цвет
        
                    param_dict['attributes'].append(self.get_attributes(9163, sex)) # пол
                    param_dict['attributes'].append(self.get_attributes(85, "Нет бренда")) # бренд
                    # param_dict['attributes'].append(self.get_attributes(9070, "true")) # признаки 18+
                    param_dict['attributes'].append(self.get_attributes(8229, attributes_type)) # тип TODO доработать в будущев в завсисимомсти от категории
                    param_dict['attributes'].append(self.get_attributes(4191, text)) # описание продукта
                    param_dict['attributes'].append(self.get_attributes(4495, "На любой сезон")) # сезон
                    param_dict['attributes'].append(self.get_attributes(9048, mod)) # модель

                    lists["items"].append(param_dict)

                for size in sizes: # все категории одежды
                    i += 1
                    param_dict = {
                        "attributes": [],
                        "barcode": "",
                        "category_id": category_id,
                        "color_image": "",
                        "complex_attributes": [ ],
                        "depth": 30,
                        "dimension_unit": "mm",
                        "height": 300,
                        "images": images,
                        "images360": [ ],
                        "name": name,
                        "offer_id": offer_id + '_' + str(i),
                        "old_price": "",
                        "pdf_list": [ ],
                        "premium_price": "",
                        "price": price,
                        "primary_image": primary_image,
                        "vat": "0.1",
                        "weight": 100,
                        "weight_unit": "g",
                        "width": 250
                    }
                
                    sex = u'Женский' if categorys_product[0].sex == 'female' else u'Мужской'

                    param_dict['attributes'].append(self.get_attributes(8292, vendor_code)) #обьеденить на одной карточке
                    for color in COLORS_MAP[color]:
                        param_dict['attributes'].append(self.get_attributes(10096, color)) # цвет
                    
                    if sex == u'Женский':
                        param_dict['attributes'].append(self.get_attributes(4295, SIZES_FAMELE_MAP[size])) # размер женский
                    else:
                        param_dict['attributes'].append(self.get_attributes(4295, SIZES_MEN_MAP[size])) # размер мужской
                    
                    param_dict['attributes'].append(self.get_attributes(9163, sex)) # пол
                    param_dict['attributes'].append(self.get_attributes(31, "Нет бренда")) # бренд
                    # param_dict['attributes'].append(self.get_attributes(9070, "true")) # признаки 18+
                    param_dict['attributes'].append(self.get_attributes(8229, attributes_type)) # тип TODO доработать в будущев в завсисимомсти от категории
                    param_dict['attributes'].append(self.get_attributes(4191, text)) # описание продукта
                    param_dict['attributes'].append(self.get_attributes(4495, "На любой сезон")) # сезон
                    param_dict['attributes'].append(self.get_attributes(12121, "6108 - Женские, для девочек: сорочка ночная, халат, пеньюар, неглиже, термобелье, комплект нижнего белья, трусы, топ-бра, пижама, кигуруми, эротическое белье т.д.")) # Код ОКПД/ТН ВЭД для обуви 

                    lists["items"].append(param_dict)

                for shueze_size in shueze_sizes: # обувь
                    i += 1
                    param_dict = {
                        "attributes": [],
                        "barcode": "",
                        "category_id": category_id,
                        "color_image": "",
                        "complex_attributes": [ ],
                        "depth": 30,
                        "dimension_unit": "mm",
                        "height": 300,
                        "images": images,
                        "images360": [ ],
                        "name": name,
                        "offer_id": offer_id + '_' + str(i),
                        "old_price": "",
                        "pdf_list": [ ],
                        "premium_price": "",
                        "price": price,
                        "primary_image": primary_image,
                        "vat": "0.1",
                        "weight": 100,
                        "weight_unit": "g",
                        "width": 250
                    }
                
                    sex = u'Женский' if categorys_product[0].sex == 'female' else u'Мужской'

                    param_dict['attributes'].append(self.get_attributes(8292, vendor_code)) #обьеденить на одной карточке
                    for color in COLORS_MAP[color]:
                        param_dict['attributes'].append(self.get_attributes(10096, color)) # цвет
                    
                    param_dict['attributes'].append(self.get_attributes(4298, shueze_size)) # размер росийский
                    
                    
                    param_dict['attributes'].append(self.get_attributes(9163, sex)) # пол
                    param_dict['attributes'].append(self.get_attributes(31, "Нет бренда")) # бренд
                    # param_dict['attributes'].append(self.get_attributes(9070, "true")) # признаки 18+
                    param_dict['attributes'].append(self.get_attributes(8229, attributes_type)) # тип TODO доработать в будущев в завсисимомсти от категории
                    param_dict['attributes'].append(self.get_attributes(4191, text)) # описание продукта
                    param_dict['attributes'].append(self.get_attributes(4495, "На любой сезон")) # сезон
                    param_dict['attributes'].append(self.get_attributes(12121, " ОКПД 2 - 15.20.11.124 - Сапожки и полусапожки из полимерных материалов ")) # Код ОКПД/ТН ВЭД для обуви 

                    lists["items"].append(param_dict)


                    
            
            response = requests.post(self.url, data=json.dumps(lists), headers=self.headers)
            print("product id:", product.id, response, response.json())
        except Exception as e:
            print('Error ', e)