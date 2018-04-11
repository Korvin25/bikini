# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.utils.html import strip_tags

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment

from .models import Product, ProductOption, ProductExtraOption


def dump_catalog_products():
    book = Workbook()

    BOLD = Font(bold=True)
    CENTER = Alignment(horizontal='center', vertical='center')
    WRAP_TEXT = Alignment(wrap_text=True)

    # создаем две вкладки
    s1 = book.active
    s1.title = 'Заголовки'
    s2 = book.create_sheet('Тексты')

    # заголовки столбцов
    for s in [s1, s2]:
        s.append(('ID', 'Russian', 'English'))
        for id in ['A1', 'B1', 'C1']:
            s[id].font = BOLD
            s[id].alignment = CENTER

    # пишем тексты товаров, вариантов и доп.товаров
    products = Product.objects.all().prefetch_related('options', 'extra_options').order_by('id')
    for p in products:
        _id = '{}t'.format(p.id)
        _ru = p.title_ru or ''
        _en = p.title_en or ''
        s1.append((_id, _ru, _en))

        if p.subtitle_ru:
            _id = '{}s'.format(p.id)
            _ru = p.subtitle_ru or ''
            _en = p.subtitle_en or ''
            s1.append((_id, _ru, _en))

        for o in p.options.all():
            if o.title_ru:
                _id = '{}_{}o'.format(p.id, o.id)
                _ru = o.title_ru or ''
                _en = o.title_en or ''
                s1.append((_id, _ru, _en))

        for e in p.extra_options.all():
            if e.title_ru:
                _id = '{}_{}e'.format(p.id, e.id)
                _ru = e.title_ru or ''
                _en = e.title_en or ''
                s1.append((_id, _ru, _en))

        if p.text_ru:
            _id = '{}t'.format(p.id)
            _ru = strip_tags(p.text_ru or '').replace('&nbsp;', ' ')
            _en = strip_tags(p.text_en or '').replace('&nbsp;', ' ')
            s2.append((_id, _ru, _en))

    # ширина столбцов
    s1.column_dimensions['B'].width = 60
    s1.column_dimensions['C'].width = 60
    s2.column_dimensions['C'].width = 60
    s2.column_dimensions['B'].width = 60

    # высота строк
    for i in xrange(2, s2.max_row+1):
        # s2.row_dimensions[i].height = 100
        s2['B{}'.format(i)].alignment = WRAP_TEXT
        s2['C{}'.format(i)].alignment = WRAP_TEXT

    # пишем в файл
    now_str = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = 'static/temp/{}_catalog.xlsx'.format(now_str)
    book.save(filename)
    book.close()
    print filename


def load_catalog(filename='apps/catalog/tempo/catalog_en.xlsx'):
    book = load_workbook(filename)

    # заголовки
    s1 = book.active
    for row in s1:
        _id = row[0].value
        _title = row[2].value

        try:
            if _id.endswith('t'):
                product_id = _id[:-1]
                product = Product.objects.get(id=product_id)
                product.title_en = _title
                product.save()

            elif _id.endswith('s'):
                product_id = _id[:-1]
                product = Product.objects.get(id=product_id)
                product.subtitle_en = _title
                product.save()

            elif _id.endswith('o'):
                o_id = _id[:-1]
                product_id, option_id = o_id.split('_')
                option = ProductOption.objects.get(id=option_id, product_id=product_id)
                option.title_en = _title
                option.save()

            elif _id.endswith('e'):
                e_id = _id[:-1]
                product_id, option_id = e_id.split('_')
                option = ProductExtraOption.objects.get(id=option_id, product_id=product_id)
                option.title_en = _title
                option.save()

            else:
                raise ValueError('Error in ID')

        except (ValueError, Product.DoesNotExist, ProductOption.DoesNotExist, ProductExtraOption.DoesNotExist) as exc:
            print '{} "{}" | {}'.format(_id, _title, exc)

        else:
            print '{} "{}" | DONE'.format(_id, _title)

    # тексты
    # TODO

    print 'done'
