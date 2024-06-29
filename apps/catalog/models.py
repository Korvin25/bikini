# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import json

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Min, Max
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer
from filer.fields.image import FilerImageField
from sortedm2m.fields import SortedManyToManyField

from ..core.templatetags.core_tags import to_price
from ..core.regions_utils import region_field
from ..core.utils import with_watermark
from ..currency.models import EUR, USD
from ..currency.utils import currency_price, get_price_from_rub
from ..settings.models import SEOSetting, MetatagModel
from ..feed.mapping import COLOR_CHOICES

# === Атрибуты (справочники) ===

class Attribute(models.Model):
    ATTRIBUTE_TYPES = (
        ('color', 'цвет'),
        ('size', 'размер'),
        ('style', 'фасон'),
        ('text', 'текст'),
    )
    POSITION_CHOICES = (
        ('all', 'все'),
        ('bottom', 'низ'),
        ('top', 'верх'),
    )
    DISPLAY_TYPES = (
        (3, 'в общем фильтре'),
        (2, 'в фильтре категории'),
        (1, 'на странице товара'),
        (0, 'откл.'),
    )
    CATEGORY_CHOICES = (
        ('primary', 'основные'),
        ('extra', 'дополнительные'),
    )
    admin_title = models.CharField('Название (в админке)', max_length=255)
    title = models.CharField('Название (на сайте)', max_length=255)
    slug = models.SlugField('В URL', help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
                                                  <br><br>примеры:<br>- color<br>- top_w<br>- bottom_size''', unique=True)
    attr_type = models.CharField('Тип', max_length=7, choices=ATTRIBUTE_TYPES)
    neighbor = models.ForeignKey('self', verbose_name='Соседний атрибут', null=True, blank=True,
                                 limit_choices_to={'attr_type': 'size'},
                                 help_text='выводится рядом на странице товара', related_name='from_neighbor')
    category = models.CharField('Категория', max_length=7, choices=CATEGORY_CHOICES)
    display_type = models.SmallIntegerField('Тип показа', choices=DISPLAY_TYPES, default=3)
    order = models.IntegerField('Порядок', default=10)

    # old and unused:
    position = models.CharField('Расположение', max_length=7, choices=POSITION_CHOICES, default='all')
    add_to_price = models.BooleanField('Прибавлять к цене', default=False, help_text='для дополнительных атрибутов')

    class Meta:
        ordering = ['-category', 'order', 'id', ]
        verbose_name = 'атрибут'
        verbose_name_plural = 'атрибуты'

    def __unicode__(self):
        return self.admin_title

    def save(self, *args, **kwargs):
        self.slug = (self.slug or '').replace('-', '_')
        if self.category == 'extra' and self.display_type > 1:
            self.display_type = 1
        return super(Attribute, self).save(*args, **kwargs)

    def set_neighbor(self, obj):
        """
        Реализуем аналог symmetrical=True у OneToOneField
        """
        self.neighbor = obj
        self.save()

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты'

    @classmethod
    def get_attrs_list(cls, qs):
        attrs = qs.prefetch_related('options').all()
        attrs = [{
            'title': attr.admin_title,
            'slug': attr.slug,
            'choices': [(option.id, option.get_label(attr_type=attr.attr_type)) for option in attr.options.all()],
        } for attr in attrs]
        return attrs


class AttributeOption(models.Model):
    attribute = models.ForeignKey(Attribute, verbose_name='Атрибут', related_name='options')
    title = models.CharField('Название', max_length=255)
    picture = ThumbnailerImageField('Картинка', upload_to='catalog/attributes/', blank=True)
    color = ColorField('Цвет', blank=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'вариант'
        verbose_name_plural = 'варианты'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.attribute:
            attr_type = self.attribute.attr_type
            if attr_type != 'color':
                self.color = ''
            if attr_type not in ['style', 'color']:
                self.picture = ''
        return super(AttributeOption, self).save(*args, **kwargs)

    def get_placeholder_image(self, image_attrs='', dimension=35, image_src='', border=True):
        if not image_src:
            image_src = 'http://via.placeholder.com/{}/{}'.format(dimension, image_attrs)
        style = 'border-radius: {}px'.format(dimension)
        if border:
            style = '{}; border: 1px solid black'.format(style)
        return '''<img src="{0}"
                       style="height: {1}px; width: {1}px; {2}"
                       title="{3}">'''.format(image_src, dimension, style, self.title)

    @property
    def admin_picture_url(self):
        try:
            return self.picture['admin_attribute_option'].url if self.picture else ''
        except:
            return ''

    @mark_safe
    def admin_show_picture(self):
        return (self.get_placeholder_image(image_src=self.admin_picture_url, dimension=200, border=False)
                if self.picture else '-')
    admin_show_picture.allow_tags = True
    admin_show_picture.short_description = 'Превью'

    @property
    def picture_url(self):
        return self.picture['attribute_option'].url if self.picture else ''

    @property
    def detail_picture_url(self):
        return self.picture['attribute_option_detail'].url if self.picture else ''

    def get_label(self, attr_type=None):
        attr_type = attr_type or self.attribute.attr_type
        label = (self.get_placeholder_image(image_src=self.admin_picture_url, dimension=35)
                 if (attr_type == 'color' and self.picture)
                 else self.get_placeholder_image('{0}/{0}'.format(self.color[1:]))
                 if (attr_type == 'color' and self.color)
                 else self.get_placeholder_image('ffffff/000000/?text={}'.format(self.title), 45)
                 if attr_type == 'size'
                 else self.get_placeholder_image(image_src=self.admin_picture_url, dimension=200, border=False)
                 if (attr_type == 'style' and self.picture)
                 else self.title)
        if self.color or self.picture:
            label = '{}&nbsp;&nbsp;{}'.format(label, self.title)
        return mark_safe(label)

    @property
    def style_photo_url(self):
        return self.picture['product_style'].url if self.picture else ''

    @property
    def is_one_size(self):
        return self.title.lower() == 'one size'

    # @property
    # def color_style(self):
    #     style = ('background: url("{}");'.format(self.picture_url) if self.picture
    #              else 'background-color: {};'.format(self.color))
    #     return mark_safe(style)


class ExtraProduct(models.Model):
    admin_title = models.CharField('Название (в админке)', max_length=255)
    title = models.CharField('Название (на сайте)', max_length=255)
    slug = models.SlugField('В URL', help_text='''уникальное поле; принимаются английские буквы, цифры и символ "_"
                                                  <br><br>примеры:<br>- color<br>- top_w<br>- bottom_size''', unique=True)
    order = models.IntegerField('Порядок', default=10)
    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='extra_products',
                                       limit_choices_to={'category': 'extra'})

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'атрибуты: дополнительные товары'

    def __unicode__(self):
        return self.admin_title

    def save(self, *args, **kwargs):
        self.slug = (self.slug or '').replace('-', '_')
        return super(ExtraProduct, self).save(*args, **kwargs)

    def show_attributes(self):
        return list(self.attributes.values_list('admin_title', flat=True))
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self):
        return self.attributes.filter(category='extra')

    def get_attrs_list(self):
        qs = self.get_attributes_qs()
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self):
        qs = self.get_attributes_qs()
        return list(qs.values_list('slug', flat=True))

    @classmethod
    def get_all_attributes_qs(cls, qs=None):
        qs = qs or ExtraProduct.objects.all()
        return Attribute.objects.filter(extra_products__in=qs)

    @classmethod
    def get_all_attrs_list(cls, qs=None):
        qs = cls.get_all_attributes_qs(qs)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    @classmethod
    def get_all_attrs_slugs(cls, qs=None):
        qs = cls.get_all_attributes_qs(qs)
        return list(qs.values_list('slug', flat=True))


# === Категории ===

class Category(MetatagModel):
    SEX_CHOICES = (
        ('female', 'Женщинам'),
        ('male', 'Мужчинам'),
    )
    title = models.CharField('Название', max_length=255)
    title_yandex = models.CharField('Название для Яндекса', max_length=255, blank=True, null=True)
    ozon_category_id = models.PositiveIntegerField('ID категории Ozon', blank=True, null=True)
    slug = models.SlugField('В URL', max_length=127)
    sex = models.CharField('Пол', max_length=7, choices=SEX_CHOICES, default='female')
    order = models.IntegerField('Порядок', default=10)
    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='categories', blank=True,
                                       limit_choices_to={'category': 'primary'})
    is_shown = models.BooleanField('Показывать на сайте', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('sex', 'slug')]
        ordering = ['sex', 'order', 'id', ]
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __unicode__(self):
        return '({}) {}'.format(self.show_sex(), self.title)

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        seo_key = {
            'female': 'women',
            'male': 'men',
        }.get(self.sex, '')
        SEOSetting.objects.get(key=seo_key).save()

        if not self.title_yandex:
            self.title_yandex = self.title
            
        return super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        reverse_name = {
            'female': 'women_category',
            'male': 'men_category',
        }.get(self.sex, '')
        return reverse(reverse_name, kwargs={'slug': self.slug})

    def get_title(self):
        SEX_TITLES = {
            'female': 'Женщинам',
            'male': 'Мужчинам',
        }
        return '{} — {}'.format(self.title, SEX_TITLES.get(self.sex))

    def get_h1_title(self):
        return self.title

    def show_sex(self):
        return {
            'female': 'Ж',
            'male': 'М',
        }.get(self.sex, '')
    show_sex.allow_tags = True
    show_sex.short_description = 'Пол'

    def show_attributes(self):
        return list(self.attributes.values_list('admin_title', flat=True))
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self, filter='primary'):
        # filter in ['primary', 'photos',]
        qs = self.attributes
        qs = (qs.filter(category='primary') if filter == 'primary'
              # else qs.filter(category='extra') if filter == 'extra'
              else qs.filter(attr_type__in=['color', 'style']) if filter == 'photos'
              else qs)
        return qs

    def get_attrs_list(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        return list(qs.values_list('slug', flat=True))


# === Дополнительные товары + сертификаты ===

class AdditionalProduct(models.Model):
    """
    switched off
    """
    title = models.CharField('Название', max_length=255)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    photo = ThumbnailerImageField('Фото', upload_to='catalog/products/', blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    show = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'товары: дополнительные товары'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        return currency_price(self)


class Certificate(models.Model):
    title = models.CharField('Название', max_length=255)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    show = models.BooleanField('Показывать на сайте', default=True)

    class Meta:
        ordering = ['price_rub', 'id', ]
        verbose_name = 'сертификат'
        verbose_name_plural = 'товары: сертификаты'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        SEOSetting.objects.get(key='certificate').save()
        return super(Certificate, self).save(*args, **kwargs)

    @property
    def price(self):
        return currency_price(self)

    @property
    def cart_cover_thumb(self):
        return '/static/images/certificate/certificate_131x86.png'


class GiftWrapping(models.Model):
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'подарочная упаковка'
        verbose_name_plural = 'подарочная упаковка'

    def __unicode__(self):
        return '#1'

    def show_name(self):
        return 'Подарочная упаковка'
    show_name.allow_tags = True
    show_name.short_description = ''

    @classmethod
    def get_prices(cls):
        prices = {
            'rub': Decimal(0.0),
            'eur': Decimal(0.0),
            'usd': Decimal(0.0),
        }
        obj = cls.objects.first()
        if obj:
            prices['rub'] = obj.price_rub
            prices['eur'] = obj.price_eur
            prices['usd'] = obj.price_usd
        return prices

    @classmethod
    def get_price(cls):
        obj = cls.objects.first()
        return currency_price(obj) if obj else Decimal(0.0)


# === Товары ===

class Product(MetatagModel):
    categories = models.ManyToManyField(Category, verbose_name='Категории', related_name='products')
    installment = models.BooleanField('Доступна рассрочка', default=False)
    title = models.CharField('Название', max_length=255)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    ozone_type = models.CharField('Тип Ozon', max_length=255, blank=True, null=True, help_text='Нужен для того чтобы, более точно передать тип товара в Ozon, eсли не заполнено, то передается название первой рубрики, которой принадлежит товар.')
    ozone_ocpd = models.CharField('Озон Код ОКПД/ТН ВЭД', max_length=512, blank=True, null=True, help_text='Указать если значение по умолчанию не подошло.')
    slug = models.SlugField('В URL', max_length=127)
    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    # photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    photo_f = FilerImageField(verbose_name='Фото')
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    text = RichTextUploadingField('Текст', blank=True, null=True)

    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))
    show = models.BooleanField('Показывать на сайте', default=True)
    show_at_yandex = models.BooleanField('Добавить в маркетплейс', default=True)
    retailcrm = models.BooleanField('Добавить в retailcrm', default=True)
    show_at_homepage = models.BooleanField('Показывать на главной', default=False)
    order_at_homepage = models.IntegerField('Порядок на главной', default=10)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    attrs = JSONField(default=dict)

    is_on_sale = models.BooleanField('Есть скидка?', default=False)
    sale_percent = models.PositiveSmallIntegerField('Скидка, %', default=0)
    show_only_on_sale = models.BooleanField('Отображать только в категории SALE', default=False)
    sale_price_rub = models.DecimalField('Цена со скидкой, руб.', max_digits=9, decimal_places=2, null=True, blank=True)
    sale_price_eur = models.DecimalField('Цена со скидкой, eur.', max_digits=9, decimal_places=2, null=True, blank=True)
    sale_price_usd = models.DecimalField('Цена со скидкой, usd.', max_digits=9, decimal_places=2, null=True, blank=True)

    additional_products = models.ManyToManyField(AdditionalProduct, blank=True,
                                                 verbose_name='Дополнительные товары', related_name='from_additional')
    associated_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                                 verbose_name='Сопутствующие товары', related_name='from_associated')
    also_products = models.ManyToManyField('self', symmetrical=False, blank=True,
                                           verbose_name='С этим товаром также покупают', related_name='from_also')

    attributes = SortedManyToManyField(Attribute, verbose_name='Атрибуты', related_name='products', blank=True,
                                       limit_choices_to={'category': 'primary'})

    class Meta:
        ordering = ['order', '-id', ]
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __unicode__(self):
        return self.title

    def _get_sale_price(self, currency):
        price = None
        if self.is_on_sale:
            price = float(getattr(self, 'price_{}'.format(currency)))
            price = price*(100.-self.sale_percent)/100.
            price = round(price*100)/100
        return price

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        """
        self.is_on_sale = not (self.sale_percent == 0)
        for c in ['rub', 'eur', 'usd']:
            setattr(self, 'sale_price_{}'.format(c), self._get_sale_price(c))
        s = super(Product, self).save(*args, **kwargs)
        for cat in self.categories.all():
            cat.save()
        return s

    # def save(self, *args, **kwargs):
    #     init_attributes = (True if (not self.id and getattr(self, 'category', None))
    #                       else False)
    #     s = super(Product, self).save(*args, **kwargs)
    #     if init_attributes:
    #         self.set_attributes_from_category(self.category)
    #     return s

    @classmethod
    def shown(cls):
        return cls.objects.prefetch_related('categories')\
                          .filter(categories__is_shown=True)\
                          .distinct()

    @property
    def shown_categories(self):
        return self.categories.filter(is_shown=True)

    def get_absolute_url(self, category=None, sex=None):
        category = category or (self.shown_categories.first() if not sex
                                else self.shown_categories.filter(sex=sex).first())
        if not category and self.categories.count():
            category = self.categories.first()
        return ('{}{}-{}/'.format(category.get_absolute_url(), self.slug, self.id) if category
                else None)

    # def get_title(self):
    #     return '{} — {}'.format(self.title, self.category.get_title())

    def get_meta_title(self, category=None):
        meta_title = region_field(self, 'meta_title')
        if meta_title:
            return meta_title
        category = category or self.categories.first()
        return '{} — {}'.format(self.title, category.get_meta_title())

    def get_text(self):
        # return self.seo_text or self.text
        return self.text

    # def set_attributes_from_category(self, category):
    #     self.attributes = category.attributes.all()
    #     self.set_attrs()

    @property
    def shown_also_products(self):
        return self.also_products.prefetch_related('categories')\
                                 .filter(show=True, categories__is_shown=True)\
                                 .exclude(id=self.id)\
                                 .distinct()

    def set_attributes_from_categories(self, categories_ids):
        self.attributes = Attribute.objects.filter(categories__id__in=categories_ids).distinct()
        self.set_attrs()

    def create_extra_products(self, extra_products_ids):
        extra_options_ids = []
        extra_products = ExtraProduct.objects.filter(id__in=extra_products_ids)
        for ep in extra_products:
            eo, _created = ProductExtraOption.objects.get_or_create(product_id=self.id, extra_product_id=ep.id,
                                                                    defaults={'title': ep.admin_title})
            extra_options_ids.append(eo.id)
        self.extra_options.exclude(id__in=extra_options_ids).delete()

    def has_attrs(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.attrs
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_attrs.allow_tags = True
    has_attrs.short_description = 'Есть атрибуты?'

    @property
    def price(self):
        return currency_price(self)

    @property
    def sale_price(self):
        return currency_price(self, 'sale_price')

    @property
    def cover_thumb(self):
        # return self.photo['product_cover'].url
        return get_thumbnailer(self.photo_f)['product_cover'].url

    @property
    def special_offer_cover(self):
        return get_thumbnailer(self.photo_f)['special_offer_cover'].url

    @property
    def cart_cover_thumb(self):
        return get_thumbnailer(self.photo_f)['cart_product_cover'].url

    @property
    def preview_url(self):
        # return self.photo['product_photo_preview'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_preview'].url)

    @property
    def thumb_url(self):
        # return self.photo['product_photo_thumb'].url
        return get_thumbnailer(self.photo_f)['product_photo_thumb'].url

    @property
    def big_url(self):
        # return self.photo['product_photo_big'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_big'].url)

    def get_price(self):
        return to_price(self.price)

    def get_sale_price(self):
        return to_price(self.sale_price)

    @mark_safe
    def show_sale_percent(self):
        percent = self.sale_percent
        return '{}%'.format(percent) if percent else '-'
    show_sale_percent.allow_tags = True
    show_sale_percent.short_description = 'Скидка'

    @mark_safe
    def options_instruction(self):
        return 'для заполнения вариантов сначала сохраните объект'
    options_instruction.allow_tags = True
    options_instruction.short_description = 'Варианты товара'

    @mark_safe
    def extra_options_instruction(self):
        if self.id:
            return '''для заполнения дополнительных товаров сначала выберите их на
                      <a href="/admin/catalog/product/{}/change_attributes/">странице изменения атрибутов</a>'''.format(self.id)
        else:
            return '''для заполнения дополнительных товаров сначала сохраните объект,
                      а потом выберите их на странице изменения атрибутов'''.format(self.id)
    extra_options_instruction.allow_tags = True
    extra_options_instruction.short_description = 'Дополнительные товары'

    @mark_safe
    def photos_instruction(self):
        return 'для добавления фото сначала сохраните объект'
    photos_instruction.allow_tags = True
    photos_instruction.short_description = 'Фото'

    @mark_safe
    def list_categories(self):
        return ', '.join([cat.__unicode__() for cat in self.categories.all()]) or '-'
    list_categories.allow_tags = True
    list_categories.short_description = 'Категории'

    @mark_safe
    def show_categories(self):
        if self.id:
            return '{} (<a href="/admin/catalog/product/{}/change_categories/">изменить</a>)'.format(
                self.list_categories(), self.id
            )
        else:
            return '-'
    show_categories.allow_tags = True
    show_categories.short_description = 'Категории'

    # @mark_safe
    # def show_category(self):
    #     if self.id:
    #         return '{} (<a href="/admin/catalog/product/{}/change_category/">изменить</a>)'.format(
    #             self.category.__unicode__(), self.id
    #         )
    #     else:
    #         return '-'
    # show_category.allow_tags = True
    # show_category.short_description = 'Категория'

    @mark_safe
    def show_attributes(self):
        attrs_str = list(self.attributes.values_list('admin_title', flat=True))
        return '{} (<a href="/admin/catalog/product/{}/change_attributes/">изменить</a>)'.format(attrs_str, self.id)
    show_attributes.allow_tags = True
    show_attributes.short_description = 'Атрибуты'

    def get_attributes_qs(self, filter='primary'):
        # filter in ['primary', 'photos',]
        qs = Attribute.objects.none()
        if filter == 'primary':
            qs = self.attributes
            qs = qs.filter(category='primary')
        elif filter == 'photos':
            attrs_ids = set(self.attributes.values_list('id', flat=True))
            extra_attrs_ids = set(self.extra_products.values_list('extra_product__attributes', flat=True))
            qs_ids = attrs_ids | extra_attrs_ids
            qs = Attribute.objects.filter(id__in=qs_ids)
            qs = qs.filter(attr_type__in=['color', 'style'])
        return qs

    def get_attrs_list(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        attrs = Attribute.get_attrs_list(qs)
        return attrs

    def get_attrs_slugs(self, filter='primary'):
        qs = self.get_attributes_qs(filter=filter)
        return list(qs.values_list('slug', flat=True))

    def set_attrs(self):
        attrs = {slug: [] for slug in self.get_attrs_slugs()}
        for _attrs in self.options.values_list('attrs', flat=True):
            for k, v in _attrs.iteritems():
                if isinstance(v, list):
                    if k in attrs:
                        attrs[k].extend(v)
        attrs = {k: list(set(v)) for k, v in attrs.iteritems()}
        self.attrs = attrs
        self.save()

    def get_placeholder_image(self, image_attrs='', dimension=35, image_src='', border=True):
        if not image_src:
            image_src = 'http://via.placeholder.com/{}/{}'.format(dimension, image_attrs)
        style = 'border-radius: {}px'.format(dimension)
        if border:
            style = '{}; border: 1px solid black'.format(style)
        return '''<img src="{0}"
                       style="height: {1}px; width: {1}px; {2}"
                       title="{3}">'''.format(image_src, dimension, style, self.title)

    @property
    def admin_photo_url(self):
        # return self.photo['admin_product_photo'].url if self.photo else ''
        return get_thumbnailer(self.photo_f)['admin_product_photo'].url

    # @mark_safe
    # def admin_show_photo(self):
    #     return ('<a href="{}" target="_blank"><img src="{}"></a>'.format(self.photo.url, self.admin_photo_url)
    #             if self.photo else '-')
    # admin_show_photo.allow_tags = True
    # admin_show_photo.short_description = 'Превью'

    @property
    def extra_products(self):
        extra_products = self.extra_options.prefetch_related('extra_product', 'extra_product__attributes').all()
        # return [extra_p for extra_p in extra_products if extra_p.attrs]
        return extra_products.filter(attrs__gt={})

    @property
    def extra_products_f(self):
        extra_products = self.extra_options.all()
        return extra_products.filter(attrs__gt={})

    @property
    def attrs_json(self):
        return json.dumps(self.attrs)

    @property
    def empty_attrs_json(self):
        return json.dumps({k: [] for k,v in self.attrs.iteritems()})

    @property
    def in_stock_counts(self):
        return self.options.all().aggregate(Min('in_stock'), Max('in_stock'))

    @mark_safe
    def get_in_stock(self):

        def _get(x):
            return x if x is not None else '-'

        in_stock_counts = self.in_stock_counts
        return '{} / {}'.format(_get(in_stock_counts['in_stock__min']), _get(in_stock_counts['in_stock__max']))
    get_in_stock.allow_tags = True
    get_in_stock.short_description = 'Кол-во товара (min/max)'


class ProductOption(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='options')
    title = models.CharField('Название', max_length=255)

    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0,
                                    help_text='оставьте цены пустыми, чтобы использовать цену родительского товара')
    in_stock = models.SmallIntegerField('Количество на складе', default=100)

    attrs = JSONField(default=dict)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'вариант'
        verbose_name_plural = 'варианты товара'

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        return currency_price(self)


class ProductExtraOption(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='extra_options')
    extra_product = models.ForeignKey(ExtraProduct, verbose_name='Дополнительный товар', related_name='extra_options')
    title = models.CharField('Название', max_length=255)

    vendor_code = models.CharField('Артикул', max_length=255, blank=True)
    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0)
    in_stock = models.SmallIntegerField('Количество на складе', default=100)

    attrs = JSONField(default=dict)

    class Meta:
        unique_together = [('product', 'extra_product')]
        ordering = ['id', ]
        verbose_name = 'дополнительный товар'
        verbose_name_plural = 'дополнительные товары'

    def __unicode__(self):
        return self.title

    @mark_safe
    def attrs_instruction(self):
        return 'для заполнения атрибутов сначала выберите тип дополнительного товара и сохраните объект'
    attrs_instruction.allow_tags = True
    attrs_instruction.short_description = 'Атрибуты'

    @property
    def price(self):
        return currency_price(self)


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='photos')
    title = models.CharField('Название', blank=True, max_length=255, help_text='необязательно; для показа в админке')
    # photo = ThumbnailerImageField('Фото', upload_to='catalog/products/')
    photo_f = FilerImageField(verbose_name='Фото')
    attrs = JSONField(default=dict)
    order = models.IntegerField('Порядок', default=10)
    color_ozon = models.CharField('Цвет для Озон', choices=COLOR_CHOICES, blank=True, null=True, max_length=100)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'фото'
        verbose_name_plural = 'фото'

    def __unicode__(self):
        return '#{}: {}'.format(self.id, self.title or self.photo_f.original_filename)

    @property
    def preview_url(self):
        # return self.photo['product_photo_preview'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_preview'].url)

    @property
    def thumb_url(self):
        # return self.photo['product_photo_thumb'].url
        return get_thumbnailer(self.photo_f)['product_photo_thumb'].url

    @property
    def big_url(self):
        # return self.photo['product_photo_big'].url
        return with_watermark(get_thumbnailer(self.photo_f)['product_photo_big'].url)

    @property
    def style_photo_url(self):
        # return self.photo['product_style'].url
        return get_thumbnailer(self.photo_f)['product_style'].url

    @property
    def attrs_json(self):
        return json.dumps(self.attrs)

    # @property
    # def admin_photo_url(self):
    #     return self.photo['admin_product_photo'].url if self.photo else ''

    # @mark_safe
    # def admin_show_photo(self):
    #     return ('<a href="{}" target="_blank"><img src="{}"></a>'.format(self.photo.url, self.admin_photo_url)
    #             if self.photo else '-')
    # admin_show_photo.allow_tags = True
    # admin_show_photo.short_description = 'Превью'


class ProductTab(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    text = RichTextUploadingField('Текст', blank=True, help_text='текст перед секциями')
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'вкладка'
        verbose_name_plural = 'страница товара: общие вкладки'

    def __unicode__(self):
        return self.title

    @property
    def shown_sections(self):
        return self.sections.filter(show=True)

    def show_sections_count(self):
        return self.sections.count()
    show_sections_count.allow_tags = True
    show_sections_count.short_description = 'Кол-во секций'


class ProductTabSection(models.Model):
    tab = models.ForeignKey(ProductTab, verbose_name='Вкладка', related_name='sections')
    title = models.CharField('Заголовок', max_length=255)
    text = RichTextUploadingField('Текст')
    show = models.BooleanField('Показывать на сайте', default=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'секция'
        verbose_name_plural = 'секции'

    def __unicode__(self):
        return self.title


# === Спец.предложения ===

class SpecialOfferCategory(models.Model):
    title = models.CharField('Название', max_length=255, help_text='для использования в админке')
    price_rub = models.DecimalField('Стоимость от, руб.', max_digits=9, decimal_places=2, default=0,
                                    unique=True)
    price_eur = models.DecimalField('Стоимость от, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Стоимость от, usd.', max_digits=9, decimal_places=2, default=0)
    is_active = models.BooleanField('Активна?', default=True)

    class Meta:
        ordering = ['-is_active', 'price_rub', ]
        verbose_name = 'категория'
        verbose_name_plural = 'спец.предложения: категории'

    def __unicode__(self):
        title = '{}{} (от {} руб.)'.format(('[откл.] ' if not self.is_active else ''),
                                           self.title,
                                           to_price(self.price_rub))
        return title

    def save(self, *args, **kwargs):
        eur_rate = EUR.get_rate()
        usd_rate = USD.get_rate()
        self.price_eur = get_price_from_rub(self.price_rub, eur_rate)
        self.price_usd = get_price_from_rub(self.price_rub, usd_rate)
        return super(SpecialOfferCategory, self).save(*args, **kwargs)

    def show_title(self):
        return self.title
    show_title.allow_tags = True
    show_title.short_description = 'Категория'

    @classmethod
    def get_category_by_summary(cls, summary=0):
        cat = None
        for category in cls.objects.filter(is_active=True).order_by('-price_rub'):
            if summary >= category.price_rub:
                cat = category
                break
        # print cat.id, cat.price_rub
        return cat


class SpecialOffer(models.Model):
    category = models.ForeignKey(SpecialOfferCategory, verbose_name='Категория', related_name='offers',
                                 default=1)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='special_offers')
    discount = models.PositiveSmallIntegerField('Скидка, %', default=50)
    is_active = models.BooleanField('Скидка активна?', default=True)

    class Meta:
        unique_together = ('category', 'product')
        ordering = ['-is_active', 'category', 'id', ]
        verbose_name = 'спец.товар'
        verbose_name_plural = 'спец.предложения: товары'

    def __unicode__(self):
        return self.product.__unicode__()

    @classmethod
    def get_offer(cls):
        return cls.get_offers().first()

    @classmethod
    def get_offers(cls, summary=None):
        offers = cls.objects.select_related('category').filter(discount__gt=0,
                                                               is_active=True,
                                                               category__is_active=True)
        if summary is not None:
            category = SpecialOfferCategory.get_category_by_summary(summary)
            offers = (offers.none() if not category
                      else offers.filter(category=category))
        return offers

    def get_discount_url(self):
        return reverse('cart_get_discount', kwargs={'pk': self.id})

    def get_offer_url(self, discount_code):
        product_url = self.product.get_absolute_url()
        return '{}discount/{}/{}/'.format(product_url, self.category_id, discount_code)


# @receiver(post_save, sender=Product)
# def update_uzon_product(sender, instance, **kwargs):
#     from ..feed.ozon_seller import OzonSeller
#     try:
#         if instance.show_at_yandex:
#             ozon_api = OzonSeller(settings.OZON_CLIENT_ID, settings.OZON_API_KEY)
#             ozon_api.update_product(instance)
#     except:
#         print('Error update ozon - product', instance.id)
