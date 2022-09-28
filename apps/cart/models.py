# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import json
import requests
import logging

from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from multiselectfield import MultiSelectField
# from paypal.standard.models import ST_PP_COMPLETED, ST_PP_PAID
from paypal.standard.ipn.models import PayPalIPN
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

from ..catalog.models import Certificate, Product, ProductOption, GiftWrapping, SpecialOffer
from ..catalog.templatetags.catalog_tags import get_product_attrs_url
from ..core.templatetags.core_tags import to_int_or_float
from ..currency.templatetags.currency_tags import with_currency, currency_compact
from ..currency.utils import get_currency, currency_price
from ..geo.models import Country
from ..hash_utils import make_hash_from_cartitem
from ..lk.email import admin_send_order_email, admin_send_low_in_stock_email, send_order_email
from ..math_utils import round_decimal
from ..utils import get_error_message


l_paypal = logging.getLogger('paypal')

ALL_LANGUAGES = [x[0] for x in settings.LANGUAGES]
LANGUAGE_CHOICES = [(x, x.upper()) for x in ALL_LANGUAGES]


class DeliveryMethod(models.Model):
    title = models.CharField('Название', max_length=511)
    short_title = models.CharField('Краткое название', max_length=63, blank=True, help_text='для вывода в личном кабинете')
    price_rub = models.DecimalField('Стоимость, руб.', max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField('Стоимость, eur.', max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField('Стоимость, usd.', max_digits=9, decimal_places=2, default=0)
    languages = MultiSelectField('Языковые разделы', max_length=255, null=True, blank=True,
                                 choices=LANGUAGE_CHOICES, default=ALL_LANGUAGES)
    is_enabled = models.BooleanField('Включен?', default=True)
    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'способ доставки'
        verbose_name_plural = 'способы доставки'

    def __unicode__(self):
        return self.title

    def get_short_title(self):
        return self.short_title or self.title

    @property
    def price(self):
        return currency_price(self)

    def show_payment_methods(self):
        return ', '.join(list(self.payment_methods.values_list('title', flat=True))) or '-'
    show_payment_methods.allow_tags = True
    show_payment_methods.short_description = 'Способы оплаты'

    def show_languages(self):
        return ', '.join(self.languages) or '-'
    show_languages.allow_tags = True
    show_languages.short_description = 'Языковые разделы'

    @property
    def payment_ids(self):
        return list(self.payment_methods.values_list('id', flat=True))


class PaymentMethod(models.Model):
    PAYMENT_TYPES = (
        ('yookassa', 'YooKassa'),
        ('robokassa', 'Robokassa'),
        ('paypal', 'PayPal'),
        ('offline', 'наличные'),
    )
    title = models.CharField('Название', max_length=511)
    short_title = models.CharField('Краткое название', max_length=63, blank=True, help_text='для вывода в личном кабинете')
    delivery_methods = models.ManyToManyField(DeliveryMethod, verbose_name='Способы доставки',
                                              blank=True, related_name='payment_methods')
    payment_type = models.CharField('Тип оплаты', max_length=15, choices=PAYMENT_TYPES, default='offline')
    languages = MultiSelectField('Языковые разделы', max_length=255, null=True, blank=True,
                                 choices=LANGUAGE_CHOICES, default=ALL_LANGUAGES)
    is_enabled = models.BooleanField('Включен?', default=True)
    order = models.PositiveSmallIntegerField(default=0, blank=False, null=False, verbose_name=mark_safe('&nbsp;&nbsp;&nbsp;&nbsp;'))

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'способ оплаты'
        verbose_name_plural = 'способы оплаты'

    def __unicode__(self):
        return self.title

    def get_short_title(self):
        return self.short_title or self.title

    def show_delivery_methods(self):
        return ', '.join(list(self.delivery_methods.values_list('title', flat=True))) or '-'
    show_delivery_methods.allow_tags = True
    show_delivery_methods.short_description = 'Способы доставки'

    def show_languages(self):
        return ', '.join(self.languages) or '-'
    show_languages.allow_tags = True
    show_languages.short_description = 'Языковые разделы'

    @property
    def delivery_ids(self):
        return list(self.delivery_methods.values_list('id', flat=True))


class Cart(models.Model):
    CURRENCY_CHOICES = (
        ('rub', 'RUB'),
        ('eur', 'EUR'),
        ('usd', 'USD'),
    )
    STATUS_CHOICES = (
        (0, 'новый'),
        (1, 'принят'),
        (2, 'отправлен'),
        (3, 'исполнен'),
        (4, 'отменен'),
    )
    profile = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Профиль', blank=True, null=True)

    creation_date = models.DateTimeField('Дата создания', auto_now_add=True)
    checked_out = models.BooleanField('Корзина оформлена', default=False)
    checkout_date = models.DateTimeField('Дата оформления', null=True, blank=True)
    payment_date = models.DateTimeField('Дата оплаты', null=True, blank=True, help_text='для оплаты онлайн')
    currency = models.CharField('Валюта', max_length=3, default='rub', choices=CURRENCY_CHOICES)

    country = models.ForeignKey(Country, verbose_name=_('Страна'), null=True, blank=True)
    city = models.CharField(_('Город'), max_length=225, null=True, blank=True)
    postal_code = models.CharField(_('Почтовый индекс'), max_length=63, null=True, blank=True)
    address = models.TextField(_('Адрес'), null=True, blank=True)
    phone = models.CharField(_('Телефон'), max_length=30, null=True, blank=True)
    name = models.CharField(_('Полное имя'), max_length=511, null=True, blank=True)

    delivery_method = models.ForeignKey(DeliveryMethod, verbose_name=_('Способ доставки'), null=True, blank=True)
    payment_method = models.ForeignKey(PaymentMethod, verbose_name=_('Способ оплаты'), null=True, blank=True)
    additional_info = models.TextField(_('Дополнительная информация'), blank=True)

    status = models.PositiveSmallIntegerField('Статус доставки', choices=STATUS_CHOICES, default=0)
    summary_rub = models.DecimalField('Сумма, руб.', max_digits=9, decimal_places=2, default=0)
    summary_eur = models.DecimalField('Сумма, eur.', max_digits=9, decimal_places=2, default=0)
    summary_usd = models.DecimalField('Сумма, usd.', max_digits=9, decimal_places=2, default=0)
    clean_cost_rub = models.DecimalField('Чистая стоимость, rub.', max_digits=9, decimal_places=2, default=0)
    clean_cost_eur = models.DecimalField('Чистая стоимость, eur.', max_digits=9, decimal_places=2, default=0)
    clean_cost_usd = models.DecimalField('Чистая стоимость, usd.', max_digits=9, decimal_places=2, default=0)
    delivery_cost_rub = models.DecimalField('Стоимость доставки, rub.', max_digits=9, decimal_places=2, default=0)
    delivery_cost_eur = models.DecimalField('Стоимость доставки, eur.', max_digits=9, decimal_places=2, default=0)
    delivery_cost_usd = models.DecimalField('Стоимость доставки, usd.', max_digits=9, decimal_places=2, default=0)
    payment_type_cost_percent = models.FloatField('Наценка за тип оплаты, %', default=0, null=True, blank=True)
    payment_type_cost_rub = models.DecimalField('Наценка за тип оплаты, rub.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    payment_type_cost_eur = models.DecimalField('Наценка за тип оплаты, eur.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    payment_type_cost_usd = models.DecimalField('Наценка за тип оплаты, usd.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)

    # --- yookassa ---
    YOO_STATUS_CHOICES = (
        ('pending', 'не оплачен'),
        ('succeeded', 'оплачен'),
        ('canceled', 'отменен'),
        ('error', 'ошибка'),
    )
    yoo_id = models.UUIDField('YooKassa: ID платежа', null=True, blank=True)
    life_pay_id = models.UUIDField('Life Pay: ID', null=True, blank=True)
    yoo_status = models.CharField('YooKassa: Статус платежа', max_length=15, null=True, blank=True, default='',
                                  choices=YOO_STATUS_CHOICES)
    yoo_paid = models.NullBooleanField('YooKassa: Оплачен?', default=None)
    yoo_redirect_url = models.URLField('YooKassa: URL для перенаправления', null=True, blank=True)
    yoo_test = models.NullBooleanField('YooKassa: Тестовый платеж?', default=None)
    yoo_popup_showed = models.BooleanField(default=False)

    # --- paypal ---
    PAYPAL_STATUS_CHOICES = (
        ('active', 'активен'),
        ('created', 'создан'),
        ('pending', 'в ожидании'),  # по дефолту
        ('processed', 'обработан'),  # в случае успеха
        ('in-progress', 'в ходе выполнения'),
        ('completed', 'оплачен'),
        ('paid', 'оплачен'),
        ('cancelled', 'оплата отменена'),
        ('denied', 'отказано'),
        ('refused', 'отказано'),
        ('declined', 'отклонен'),
        ('cleared', 'удален'),
        ('failed', 'не удался'),
        ('expired', 'истек'),
        ('refunded', 'возвращен'),
        ('partially_refunded', 'частично возвращен'),
        ('reversed', 'обратный'),
        ('canceled_reversal', 'отмененный обратный'),
        ('rewarded', 'награжден'),
        ('unclaimed', 'невостребован'),
        ('uncleared', 'неочищен'),
        ('voided', 'аннулирован'),
        ('error', 'ошибка'),
    )
    paypal_txn_id = models.CharField('PayPal: ID транзакции', max_length=31, null=True, blank=True)
    paypal_txn_type = models.CharField('PayPal: Тип транзакции', max_length=31, null=True, blank=True)
    paypal_status = models.CharField('PayPal: Статус платежа', max_length=15, null=True, blank=True, default='',
                                     choices=PAYPAL_STATUS_CHOICES)
    paypal_paid = models.NullBooleanField('PayPal: Оплачен?', default=None)
    paypal_popup_showed = models.BooleanField(default=False)
    paypal_ipn_obj = models.ForeignKey(PayPalIPN, null=True, blank=True)
    paypal_approve_token = models.CharField('PayPal: Токен подтверждения', max_length=31, blank=True, default='')
    paypal_cancel_token = models.CharField('PayPal: Токен отмены', max_length=31, blank=True, default='')

    robokassa_id = models.CharField('RoboKassa: ID платежа', max_length=31, null=True, blank=True)
    robokassa_status = models.CharField('RoboKassa: Статус платежа', max_length=15, null=True, blank=True, default='', choices=YOO_STATUS_CHOICES)           
    robokassa_paid = models.NullBooleanField('RoboKassa: Оплачен?', default=None)
    robokassa_url = models.CharField('RoboKassa: URL', max_length=1000, null=True, blank=True)
    robokassa_token = models.CharField('RoboKassa: Токен', max_length=310, blank=True, default='', null=True,)

    # --- яндекс.метрика ---
    TRAFFIC_SOURCE_CHOICES = (
        ('organic', 'Переходы из поисковых систем'),
        ('social', 'Переходы из социальных сетей'),
        ('ad', 'Переходы по рекламе'),
        ('direct', 'Прямые заходы'),
        ('internal', 'Внутренние переходы'),
        ('referral', 'Переходы по ссылкам на сайтах'),
        ('saved', 'Переходы с сохранённых страниц'),
    )
    ym_client_id = models.CharField('Идентификатор посетителя', max_length=63, null=True, blank=True)
    ym_source = models.CharField('Источник трафика', max_length=15, choices=TRAFFIC_SOURCE_CHOICES, null=True, blank=True)
    ym_source_detailed = models.CharField('Источник трафика (детально)', max_length=127, null=True, blank=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'
        ordering = ('-checkout_date',)

    def __unicode__(self):
        # return unicode(self.creation_date)
        return self.title

    @property
    def summary(self):
        return currency_price(self, 'summary')

    @property
    def summary_c(self):
        return currency_price(self, 'summary', currency=self.currency)

    @property
    def delivery_method_price_c(self):
        return currency_price(self.delivery_method, currency=self.currency)

    @property
    def clean_cost(self):
        return currency_price(self, 'clean_cost')

    @property
    def clean_cost_c(self):
        return currency_price(self, 'clean_cost', currency=self.currency)

    @property
    def delivery_cost(self):
        return currency_price(self, 'delivery_cost')

    @property
    def delivery_cost_c(self):
        return currency_price(self, 'delivery_cost', currency=self.currency)

    @property
    def payment_type_cost(self):
        return currency_price(self, 'payment_type_cost')

    @property
    def payment_type_cost_c(self):
        return currency_price(self, 'payment_type_cost', currency=self.currency)

    def save(self, *args, **kwargs):
        if not self.checked_out:
            self.get_summary()
        return super(Cart, self).save(*args, **kwargs)

    def count(self):
        count_list = self.cartitem_set.filter(product__show=True).values_list('count', flat=True)
        result = sum(count_list) + self.certificatecartitem_set.count()
        return result
    count.allow_tags = True
    count.short_description = 'Количество товара'

    def get_summary(self):
        # сумма всех товаров в корзине
        prices = self.cartitem_set.filter(product__show=True).values('price_rub', 'price_eur', 'price_usd')
        result_rub = sum([price['price_rub'] for price in prices])
        result_eur = sum([price['price_eur'] for price in prices])
        result_usd = sum([price['price_usd'] for price in prices])

        # + сумма сертификатов в корзине
        if self.certificatecartitem_set.count():
            certificate_prices = self.certificatecartitem_set.all().values('price_rub', 'price_eur', 'price_usd')
            result_rub += sum([price['price_rub'] for price in certificate_prices])
            result_eur += sum([price['price_eur'] for price in certificate_prices])
            result_usd += sum([price['price_usd'] for price in certificate_prices])

        # (запоминаем чистую сумму)
        self.clean_cost_rub = result_rub
        self.clean_cost_eur = result_eur
        self.clean_cost_usd = result_usd

        # + добавляем стоимость доставки
        delivery_method = self.delivery_method
        if delivery_method:
            self.delivery_cost_rub = delivery_method.price_rub
            self.delivery_cost_eur = delivery_method.price_eur
            self.delivery_cost_usd = delivery_method.price_usd
            result_rub += self.delivery_cost_rub
            result_eur += self.delivery_cost_eur
            result_usd += self.delivery_cost_usd

        # + накидываем 7% за paypal
        payment_type = self.payment_type
        if payment_type == 'paypal':
            self.payment_type_cost_percent = 7.0
            _multiplier = Decimal('0.07')
            self.payment_type_cost_rub = round_decimal(result_rub*_multiplier)
            self.payment_type_cost_eur = round_decimal(result_eur*_multiplier)
            self.payment_type_cost_usd = round_decimal(result_usd*_multiplier)
            result_rub += self.payment_type_cost_rub
            result_eur += self.payment_type_cost_eur
            result_usd += self.payment_type_cost_usd
        else:
            self.payment_type_cost_percent = 0
            self.payment_type_cost_rub = 0
            self.payment_type_cost_eur = 0
            self.payment_type_cost_usd = 0

        # готово
        self.summary_rub = result_rub
        self.summary_eur = result_eur
        self.summary_usd = result_usd

    def get_yandex_currency(self):
        currency = {
            'rub': 'RUB',
            'eur': 'EUR',
            'usd': 'USD',
        }
        return currency.get(self.currency, 'RUB')

    @property
    def has_items_with_discount(self):
        discounts = self.cartitem_set.filter(product__show=True).values_list('discount', flat=True)
        with_discount = bool(sum(discounts))
        return with_discount

    def is_order_with_discount(self):
        with_discount = self.has_items_with_discount
        return ('<img src="/static/admin/img/icon-yes.svg" alt="Да">' if with_discount
                else '<img src="/static/admin/img/icon-no.svg" alt="Нет">')
    is_order_with_discount.allow_tags = True
    is_order_with_discount.short_description = 'Товары со скидкой'

    # def get_order_url(self):
    #     return reverse('profile:order', kwargs={'pk': self.id})

    def profile_with_link(self):
        p = self.profile
        if not p:
            return '-'
        link = '<a href="/admin/lk/profile/{}/change/" target="_blank">{}</a>'.format(p.id, p.__unicode__())
        return mark_safe(link)
    profile_with_link.allow_tags = True
    profile_with_link.short_description = 'Профиль'

    # def title_with_link(self):
    #     return '<a href="/admin/cart/cart/{}/change/" target="_blank">{}</a>'.format(self.id, self.title)
    # title_with_link.allow_tags = True
    # title_with_link.short_description = 'Заказ'

    def life_pay_post_request(self):
        """Удаленная фискализация.
        """
        url = u'https://sapi.life-pay.ru/cloud-print/create-receipt'
        purchase =  {
            "products": [
                {
                    "name": item.product.title, 
                    "price": float(item.product.price_rub) if not item.product.sale_price_rub else float(item.product.sale_price_rub), 
                    "quantity": item.count,
                    "item_type": 1,
                } 
                for item in self.cart_items
            ]
        }
        
        if self.show_delivery_cost_c() != u'0':
            purchase['products'].append(
                {
                    "name": u'Стоимость доставки', 
                    "price": float(self.show_delivery_cost_c()), 
                    "quantity": 1,
                    "item_type": 4,
                } 
            )
        
        for item in self.cart_items:
            if float(item.wrapping_price_rub):
                purchase['products'].append(
                {
                    "name": u'Подарочная упаковка', 
                    "price": float(item.wrapping_price_rub), 
                    "quantity": 1,
                    "item_type": 1,
                } 
            )

        headers = {}
        data = {
            'apikey': settings.LIFE_PAY_API_KEY,
            'login': settings.LIFE_PAY_API_LOGIN,
            'purchase': purchase,
            'card_amount': float(self.summary),
            'ext_id': str(self.id),
            'mode': 'email',
            'customer_email': self.profile.email,
            # 'test': 1
        }
        if self.phone:
            data['customer_phone'] = self.phone

        req = requests.post(url, headers=headers, data=json.dumps(data))
        return req.json()

    def show_profile(self):
        return self.profile or ''
    show_profile.allow_tags = True
    show_profile.short_description = 'Клиент'

    def admin_show_summary(self):
        summary = self.summary_c
        summary_with_currency = with_currency(summary, self.currency, with_title=False)
        return mark_safe(summary_with_currency)
    admin_show_summary.allow_tags = True
    admin_show_summary.short_description = 'Сумма'

    def show_delivery_method(self):
        method = self.delivery_method
        return method.get_short_title() if method else '-'
    show_delivery_method.allow_tags = True
    show_delivery_method.short_description = 'Способ доставки'

    def show_payment_method(self):
        method = self.payment_method
        return method.get_short_title() if method else '-'
    show_payment_method.allow_tags = True
    show_payment_method.short_description = 'Способ оплаты'

    def _show_value(self, value):
        value = int(value) if int(value) == value else value
        return '{0:,}'.format(value).replace(',', ' ')

    def show_clean_cost(self):
        return self._show_value(self.clean_cost)

    def show_clean_cost_c(self):
        return self._show_value(self.clean_cost_c)

    def show_summary(self):
        return self._show_value(self.summary)

    def show_summary_c(self):
        return self._show_value(self.summary_c)

    def show_delivery_cost(self):
        return self._show_value(self.delivery_cost)

    def show_delivery_cost_c(self):
        return self._show_value(self.delivery_cost_c)

    def show_payment_type_cost(self):
        return self._show_value(self.payment_type_cost)

    def show_payment_type_cost_c(self):
        return self._show_value(self.payment_type_cost_c)

    def get_order_id(self):
        return '{0:06}'.format(self.id)

    @property
    def title(self):
        return '№ {}'.format(self.number)

    @property
    def number(self):
        # TODO: покрасивше
        if not self.id:
            return '0'
        if self.id > 1000:
            return '{:,}'.format(self.id).rjust(7, '0').replace(',', ' ')
        else:
            _number = '{:03}'.format(self.id)
            return '000 {}'.format(_number)

    def show_items(self):
        template = get_template('cart/admin/admin_cart_items.html')
        data = template.render({'cart': self})
        return mark_safe(data)
    show_items.allow_tags = True
    show_items.short_description = 'Список позиций'

    @property
    def cart_items(self):
        return self.cartitem_set.filter(product__show=True).select_related('product', 'option').all()

    @property
    def certificate_items(self):
        return self.certificatecartitem_set.select_related('certificate').all()

    @property
    def payment_type(self):
        return self.payment_method.payment_type if self.payment_method else 'offline'

    @property
    def payment_status(self):
        return {
            'yookassa': self.yoo_status,
            'robokassa': self.robokassa_status,
            'paypal': self.paypal_status,
        }.get(self.payment_type, '')

    @property
    def is_pending(self):
        payment_status = self.payment_status
        return payment_status == 'pending'

    @property
    def is_canceled(self):
        payment_status = self.payment_status
        return payment_status in ['error', 'canceled', 'cancelled']

    @property
    def is_paid(self):
        return {
            'yookassa': self.yoo_paid,
            'robokassa': self.robokassa_paid,
            'paypal': self.paypal_paid,
        }.get(self.payment_type, None)

    def show_status(self):
        payment_type = self.payment_type
        status = self.get_status_display()
        if payment_type != 'offline':
            # 1
            _yoo_status = {
                'error': 'ошибка',
                'pending': 'не оплачен',
                'succeeded': 'оплачен',
                'canceled': 'оплата отменена',
            }.get(self.yoo_status, '')
            _paypal_status = self.get_paypal_status_display()
            # 2
            # 3
            _robo_status = {
                'error': 'ошибка',
                'pending': 'не оплачен',
                'succeeded': 'оплачен',
                'canceled': 'оплата отменена',
            }.get(self.robokassa_status, '')
            status_str = {
                'yookassa': _yoo_status,
                'robokassa': _robo_status,
                'paypal': _paypal_status,
            }.get(payment_type, '')
            # 3
            if status_str:
                status = (status_str if self.is_canceled
                          else '{} / {}'.format(status_str, status))
        return status
    show_status.short_description = 'Статус'
    show_status.allow_tags = True

    # -- штуки после покупки

    def send_order_emails(self):
        status = self.show_status()
        
        if not status == 'не оплачен / новый':
            admin_send_order_email(self)

        profile = self.profile
        if profile and profile.has_email: 
            if status == 'оплачен / новый' or status == 'новый':
                send_order_email(profile, obj=self)

    def update_in_stock(self, send_email=True):
        _options = []
        _extra_products = []

        items = self.cartitem_set.filter(product__show=True)
        for item in items:
            count = item.count

            option = item.option
            in_stock = option.in_stock - count
            in_stock = 0 if in_stock < 0 else in_stock
            option.in_stock = in_stock
            option.save()
            if in_stock < 5:
                _options.append({'option': option, 'product': item.product, 'in_stock': in_stock})

            extra_p_ids = item.extra_products.keys()
            if extra_p_ids:
                try:
                    extra_products = item.product.extra_options.filter(extra_product_id__in=extra_p_ids)
                except ValueError:
                    pass
                else:
                    for extra_p in extra_products:
                        in_stock = extra_p.in_stock - count
                        in_stock = 0 if in_stock < 0 else in_stock
                        extra_p.in_stock = in_stock
                        extra_p.save()
                        if in_stock < 5:
                            _extra_products.append({'extra_p': extra_p, 'product': item.product, 'in_stock': in_stock})

        if _options or _extra_products:
            admin_send_low_in_stock_email(_options, _extra_products)

    def get_specials(self):
        profile = self.profile
        specials = (SpecialOffer.get_offers(summary=self.clean_cost_rub)
                    if profile.can_get_discount
                    else SpecialOffer.objects.none())
        return specials

    def get_specials_html(self, specials=None, request=None):
        if specials is None:
            specials = self.get_specials()
        if not specials:
            return ''
        specials_template = get_template('cart/step5_specials.html')
        currency = get_currency(request=request)
        context = {'specials': specials, 'currency': currency}
        return specials_template.render(context)

    def get_paypal_paid(self):
        return self.paypal_status in ['completed', 'paid']


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender

    l_paypal.info('------ Получен сигнал от PayPal')
    l_paypal.info('[ipn_obj id: {}]'.format(ipn_obj.id))

    if ipn_obj.receiver_email != settings.PAYPAL_EMAIL:
        l_paypal.warning('email не совпадают; return')
        l_paypal.warning('------/')
        return

    try:
        cart_id = int(ipn_obj.invoice)
        cart = Cart.objects.get(id=cart_id)
        was_paid = cart.paypal_paid

        # if ipn_obj.mc_gross == cart.summary_c and ipn_obj.mc_currency.lower() == cart.currency:
        if ipn_obj.mc_currency.lower() == cart.currency:
            l_paypal.info('[cart id: {}]; обновляем...'.format(cart.id))

            cart.paypal_txn_id = ipn_obj.txn_id
            cart.paypal_txn_type = ipn_obj.txn_type
            cart.paypal_status = (ipn_obj.payment_status or '').lower()
            cart.paypal_paid = cart.get_paypal_paid()
            cart.paypal_ipn_obj = ipn_obj
            cart.save()

            l_paypal.info('  paypal_status: {}; paypal_paid: {}...'.format(cart.paypal_status, cart.paypal_paid))

            if cart.paypal_paid and not was_paid:
                l_paypal.info('  отправляем мыла об оплате...')
                # -- отправка имейлов --
                cart.send_order_emails()
                # -- остатки на складе --
                cart.update_in_stock()
            else:
                cart.send_order_emails()

            l_paypal.info('  done!')
            l_paypal.info('------/')

        else:
            raise Exception('(cart_id {}): что-то не совпадает'.format(cart.id))

    except Exception as exc:
        err_message = get_error_message(exc)
        l_paypal.error('------ Ошибка при получении сигнала: {}'.format(err_message))
        l_paypal.error('[ipn_obj id: {}]'.format(ipn_obj.id))
        l_paypal.error('[ipn_obj txn_id: {}]'.format(ipn_obj.txn_id))
        l_paypal.error('[ipn_obj payment_status: {}]'.format(ipn_obj.payment_status))
        l_paypal.error('[ipn_obj mc_gross: {}]'.format(ipn_obj.mc_gross))
        l_paypal.error('[ipn_obj mc_currency: {}]'.format(ipn_obj.mc_currency))
        l_paypal.warning('------/')


valid_ipn_received.connect(show_me_the_money)
invalid_ipn_received.connect(show_me_the_money)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, db_index=True)
    product = models.ForeignKey(Product, verbose_name='Товар', db_index=True)
    option = models.ForeignKey(ProductOption, verbose_name='Вариант')
    count = models.PositiveIntegerField('Количество')

    attrs = JSONField(default=dict)
    extra_products = JSONField(default=dict)
    hash = models.BigIntegerField(default=0, db_index=True)

    with_wrapping = models.BooleanField(default=False)
    discount = models.PositiveSmallIntegerField(default=0)

    option_price_rub = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    option_price_eur = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    option_price_usd = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    extra_price_rub = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    extra_price_eur = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    extra_price_usd = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    wrapping_price_rub = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    wrapping_price_eur = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    wrapping_price_usd = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    price_rub = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'
        ordering = ('cart', '-id',)

    def __unicode__(self):
        return '{} units of {}'.format(self.count, self.title)

    def update_price(self, *args, **kwargs):
        option = self.option
        if not self.option_price_rub == option.price_rub:
            self.option_price_rub = self.price_rub = option.price_rub
        if not self.option_price_eur == option.price_eur:
            self.option_price_eur = self.price_eur = option.price_eur
        if not self.option_price_usd == option.price_usd:
            self.option_price_usd = self.price_usd = option.price_usd
        super(CartItem, self).save(*args, **kwargs)
        self.cart.get_summary()

    @property
    def option_price(self):
        self.update_price()
        return currency_price(self, 'option_price')

    @property
    def extra_price(self):
        return currency_price(self, 'extra_price')

    @property
    def wrapping_price(self):
        return currency_price(self, 'wrapping_price')

    @property
    def price(self):
        self.update_price()
        return currency_price(self)

    @property
    def option_price_c(self):
        self.update_price()
        return currency_price(self, 'option_price', currency=self.cart.currency)

    @property
    def extra_price_c(self):
        return currency_price(self, 'extra_price', currency=self.cart.currency)

    @property
    def wrapping_price_c(self):
        return currency_price(self, 'wrapping_price', currency=self.cart.currency)

    @property
    def price_c(self):
        self.update_price()
        return currency_price(self, currency=self.cart.currency)

    @property
    def title(self):
        return self.option.title or self.product.__unicode__()

    def get_vendor_code(self):
        return self.option.vendor_code or self.product.vendor_code

    @property
    def url(self):
        return get_product_attrs_url(self.product, self.attrs, self.extra_products, self.with_wrapping, self.count)

    @classmethod
    def had_discounts(cls, cart_ids):
        return bool(cls.objects.filter(cart_id__in=cart_ids, discount__gt=0).count())

    def get_option_price(self):
        option = self.option
        self.option_price_rub = self.option_price_rub or option.price_rub
        self.option_price_eur = self.option_price_eur or option.price_eur
        self.option_price_usd = self.option_price_usd or option.price_usd

    def get_extra_price(self):
        if self.extra_price_rub and self.extra_price_eur and self.extra_price_usd:
            return

        extra_products = self.product.extra_products.filter(extra_product_id__in=self.extra_products.keys())
        prices = extra_products.values('price_rub', 'price_eur', 'price_usd')
        self.extra_price_rub = sum([price['price_rub'] for price in prices])
        self.extra_price_eur = sum([price['price_eur'] for price in prices])
        self.extra_price_usd = sum([price['price_usd'] for price in prices])

    def get_wrapping_price(self):
        price_rub = 0.0
        price_eur = 0.0
        price_usd = 0.0

        if self.with_wrapping:
            prices = GiftWrapping.get_prices()
            price_rub = prices['rub']
            price_eur = prices['eur']
            price_usd = prices['usd']

        self.wrapping_price_rub = Decimal(price_rub)
        self.wrapping_price_eur = Decimal(price_eur)
        self.wrapping_price_usd = Decimal(price_usd)

    def get_base_price(self, with_discount=True, currency=None):
        self.update_price()
        if currency is None:
            option_price = currency_price(self, 'option_price')
            extra_price = currency_price(self, 'extra_price')
        else:
            option_price = getattr(self, 'option_price_{}'.format(currency))
            extra_price = getattr(self, 'extra_price_{}'.format(currency))

        if with_discount and self.discount:
            discount_price = option_price*self.discount // 100
            option_price = Decimal(to_int_or_float(option_price - discount_price))
        return option_price+extra_price

    @property
    def base_price(self):
        return self.get_base_price()

    @property
    def base_price_without_discount(self):
        return self.get_base_price(with_discount=False)

    def count_price(self):
        price_rub = 0
        price_eur = 0
        price_usd = 0

        if self.count:
            price_rub = self.get_base_price(currency='rub')*self.count + self.wrapping_price_rub
            price_eur = self.get_base_price(currency='eur')*self.count + self.wrapping_price_eur
            price_usd = self.get_base_price(currency='usd')*self.count + self.wrapping_price_usd

        self.price_rub = price_rub
        self.price_eur = price_eur
        self.price_usd = price_usd

    @property
    def total_price_without_discount(self):
        return to_int_or_float((self.base_price_without_discount*self.count + self.wrapping_price) if self.count
                               else 0)

    def save(self, *args, **kwargs):
        self.get_option_price()
        self.get_extra_price()
        self.get_wrapping_price()
        self.count_price()
        return super(CartItem, self).save(*args, **kwargs)

    @property
    def price_int(self):
        price = self.price
        return to_int_or_float(price)

    def set_hash(self):
        hash = make_hash_from_cartitem(self.attrs, self.extra_products)
        self.hash = hash
        self.save()
        return hash


class CertificateCartItem(models.Model):
    cart = models.ForeignKey(Cart)
    certificate = models.ForeignKey(Certificate, verbose_name='Сертификат', related_name='cart_items')

    recipient_name = models.CharField('Имя получателя', max_length=255)
    recipient_email = models.EmailField('Email получателя', blank=True)
    sender_name = models.CharField('Имя отправителя', max_length=255, blank=True)
    sender_phone = models.CharField('Телефон отправителя', max_length=127)
    sender_email = models.EmailField('Email отправителя')
    message = models.TextField('Сообщение получателю', blank=True)

    send_immediately = models.BooleanField('Отправлять сразу?', default=True)
    send_date = models.DateField('Дата отправки', blank=True, null=True)

    price_rub = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price_eur = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    price_usd = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'сертификат'
        verbose_name_plural = 'сертификаты'
        ordering = ('cart', '-id',)

    def __unicode__(self):
        return self.title

    @property
    def price(self):
        return currency_price(self)

    @property
    def price_c(self):
        return currency_price(self, currency=self.cart.currency)

    @property
    def url(self):
        return '{}?_certificate={}'.format(reverse('certificate'), self.certificate_id)

    @property
    def title(self):
        label = _('Сертификат на')
        price = currency_price(self)
        currency = get_currency()
        return '{} {}'.format(label, currency_compact(price, currency))

    @property
    def title_c(self):
        label = _('Сертификат на')
        currency = self.cart.currency
        price = currency_price(self, currency=currency)
        return '{} {}'.format(label, currency_compact(price, currency))

    @property
    def count(self):
        return 1

    def get_vendor_code(self):
        return self.certificate.vendor_code

    def count_price(self):
        certificate = self.certificate
        self.price_rub = certificate.price_rub
        self.price_eur = certificate.price_eur
        self.price_usd = certificate.price_usd

    def save(self, *args, **kwargs):
        self.count_price()
        return super(CertificateCartItem, self).save(*args, **kwargs)

    @property
    def price_int(self):
        price = self.price
        return to_int_or_float(price)
