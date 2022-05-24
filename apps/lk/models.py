# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import uuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ..currency.utils import currency_price
from ..geo.models import Country
from ..hash_utils import make_hash_from_cartitem
from ..lang.utils import get_current_lang
from .mailchimp import m_add, m_update_fields, m_resubscribe, m_unsubscribe, m_remove


email_subj_list = [_('Bikinimini.ru: Сброс пароля', 'Ваш заказ на Bikinimini.ru: № %d'), ]


class UserManager(BaseUserManager):

    def create_user(self, email, password):

        if not email:
            raise ValueError('Email: required fiield')

        if not password:
            raise ValueError('Password: required field')

        user = self.model(
            email=UserManager.normalize_email(email),
        )
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

    def get_by_natural_key(self, username):
        """
        Делаем логин регистронезависимым.

        https://djangosnippets.org/snippets/1368/
        (comment by bquinn at February 12, 2014)
        """
        return self.get(email__iexact=username)


LANGUAGE_CHOICES = [(lang[0], lang[0]) for lang in settings.LANGUAGES]
MAILCHIMP_KEYS = ['name', 'address', 'phone', 'country_title', 'city', 'lang']


class Profile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email'), unique=True)
    date_joined = models.DateTimeField('Дата и время регистрации', auto_now_add=True)
    subscription = models.BooleanField('Подписан на рассылку', default=False)
    old_subscription = models.BooleanField('Previous Подписан на рассылку', default=False)
    lang = models.CharField('Язык', max_length=3, default='ru', choices=LANGUAGE_CHOICES)

    is_active = models.BooleanField('Активен?', default=True, help_text='снимите галку, чтобы заблокировать юзера')
    is_staff = models.BooleanField('Имеет доступ к админ-панели', default=False)

    # --- данные из формы в профиле ---
    country = models.ForeignKey(Country, verbose_name=_('Страна'), null=True, blank=True)
    city = models.CharField(_('Город'), max_length=225, null=True, blank=True)
    postal_code = models.CharField(_('Почтовый индекс'), max_length=63, null=True, blank=True)
    address = models.TextField(_('Адрес'), null=True, blank=True)
    phone = models.CharField(_('Телефон'), max_length=30, null=True, blank=True)
    name = models.CharField(_('Полное имя'), max_length=511, null=True, blank=True)

    delivery_method = models.ForeignKey('cart.DeliveryMethod', verbose_name=_('Способ доставки'), null=True, blank=True)
    payment_method = models.ForeignKey('cart.PaymentMethod', verbose_name=_('Способ оплаты'), null=True, blank=True)

    # --- соц.сети ---
    fb_id = models.CharField('Facebook ID', max_length=255, null=True, blank=True)
    fb_name = models.CharField('Facebook name', max_length=255, null=True, blank=True)
    fb_link = models.CharField('Facebook link', max_length=255, null=True, blank=True)
    vk_id = models.CharField('VK ID', max_length=255, null=True, blank=True)
    vk_name = models.CharField('VK name', max_length=255, null=True, blank=True)
    vk_link = models.CharField('VK link', max_length=255, null=True, blank=True)
    gp_id = models.CharField('Google+ ID', max_length=255, null=True, blank=True)
    gp_name = models.CharField('Google+ name', max_length=255, null=True, blank=True)
    gp_link = models.CharField('Google+ link', max_length=255, null=True, blank=True)
    ig_id = models.CharField('Instagram ID', max_length=255, null=True, blank=True)
    ig_name = models.CharField('Instagram name', max_length=255, null=True, blank=True)
    ig_link = models.CharField('Instagram link', max_length=255, null=True, blank=True)

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

    # --- Mailchimp ---
    mailchimp_all_hash = models.CharField(max_length=100, null=True, blank=True, editable=False, default='')
    mailchimp_tried_to_subscribe = models.BooleanField(default=False)
    mailchimp_subscribed_hash = models.CharField(max_length=100, null=True, blank=True, editable=False, default='')
    mailchimp_unsubscribed_hash = models.CharField(max_length=100, null=True, blank=True, editable=False, default='')
    mailchimp_name = models.CharField(max_length=511, null=True, blank=True, editable=False)
    mailchimp_address = models.TextField(null=True, blank=True, editable=False)
    mailchimp_phone = models.CharField(max_length=30, null=True, blank=True, editable=False)
    mailchimp_country_title = models.CharField(max_length=225, null=True, blank=True, editable=False)
    mailchimp_city = models.CharField(max_length=225, null=True, blank=True, editable=False)
    mailchimp_lang = models.CharField(max_length=3, null=True, blank=True, editable=False)

    # --- покупки со скидкой ---
    discount_code = models.CharField('Код скидки', max_length=127, null=True, blank=True)
    discount_used = models.BooleanField('Скидка использована?', default=False)

    has_email = models.BooleanField(default=True)
    has_password = models.BooleanField(default=True)
    signature = models.CharField('Login hash', max_length=50, null=True, blank=True, editable=False)
    orders_num = models.PositiveSmallIntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __unicode__(self):
        return ('{} ({}, id #{})'.format(self.name, self.email, self.id) if self.name and self.has_email
                else '{} (id #{})'.format(self.name, self.id) if self.name
                else '{} (id #{})'.format(self.email, self.id) if self.has_email
                else 'id #{}'.format(self.id))

    @property
    def country_title(self):
        return self.country.title if self.country else ''

    @property
    def fields_changed(self):
        _changed = False
        for key in MAILCHIMP_KEYS:
            _self = getattr(self, key)
            _mailchimp = getattr(self, 'mailchimp_{}'.format(key))
            _changed = _changed or (_self and _self != _mailchimp)
            if _changed is True:
                break
        return _changed

    @property
    def merge_tags(self):
        return {
            'NAME': self.name,
            'ADDRESS': self.address,
            'PHONE': self.phone,
            'CITY': self.city,
            'COUNTRY': self.country_title,
            'LANGUAGE': self.lang,
        }

    def clean_merge_tags(self, merge_tags=None):
        merge_tags = merge_tags or self.merge_tags
        return {tag: value for tag, value in self.merge_tags.items() if value}

    def update_mailchimp_fields(self):
        for key in MAILCHIMP_KEYS:
            setattr(self, 'mailchimp_{}'.format(key), getattr(self, key))

    def save(self, *args, **kwargs):
        if not self.id:
            self.lang = get_current_lang()

        if self.fields_changed:
            merge_tags = self.merge_tags
            if self.mailchimp_all_hash:
                m_update_fields(self.mailchimp_all_hash, 'all', **merge_tags)
            self.update_mailchimp_fields()

        return super(Profile, self).save(force_insert=False)

    def clear_mailchimp_fields(self):
        self.old_subscription = False
        self.mailchimp_all_hash = ''
        self.mailchimp_tried_to_subscribe = False
        self.mailchimp_subscribed_hash = ''
        self.mailchimp_unsubscribed_hash = ''
        self.mailchimp_name = None
        self.mailchimp_address = None
        self.mailchimp_phone = None
        self.mailchimp_country_title = None
        self.mailchimp_city = None
        self.mailchimp_lang = None
        self.save()

    def get_short_name(self):
        return self.name or self.email

    def get_full_name(self):
        return self.__unicode__()

    @property
    def username(self):
        return self.email

    def get_signature(self):
        self.signature = Profile.objects.make_random_password(length=40)
        self.save()
        return self.signature

    @property
    def shipping_data(self):
        data = {
            'country': self.country_id,
            'city': self.city or '',
            'postal_code': self.postal_code or '',
            'address': self.address or '',
            'phone': self.phone or '',
            'name': self.name or '',
            'email': self.email if self.has_email else '',
            'payment_method_id': self.payment_method_id,
            'delivery_method_id': self.delivery_method_id,
        }
        data = {k: v for k, v in data.iteritems() if v}
        return data

    # @property
    # def methods_data(self):
    #     data = {
    #         'payment_method_id': self.payment_method_id,
    #         'delivery_method_id': self.delivery_method_id,
    #     }
    #     data = {k: v for k, v in data.iteritems() if v}
    #     return data

    @property
    def complete_orders(self):
        return self.cart_set.filter(checked_out=True)

    @property
    def can_get_discount(self):
        # from ..cart.models import CartItem
        complete_orders = self.complete_orders.values_list('id', flat=True)
        return (True if complete_orders.count()
                else False)

    def get_discount_code(self):
        discount_code = self.discount_code
        if not discount_code:
            discount_code = self.discount_code = str(uuid.uuid4()).replace('-', '')
            self.save()
        return discount_code

    @property
    def wishlist(self):
        return list(self.wishlist_items.all().values('product_id', 'option_id', 'price_rub', 'price_eur', 'price_usd',
                                                     'attrs', 'extra_products', 'hash',))


@receiver(post_save, sender=Profile, dispatch_uid='update_mailchimp_lists')
def update_mailchimp_lists(sender, instance, **kwargs):
    profile = instance; save = False
    clean_merge_tags = None

    if not profile.mailchimp_all_hash and profile.mailchimp_tried_to_subscribe is False:
        # первоначальная подписка на mailchimp
        clean_merge_tags = clean_merge_tags or profile.clean_merge_tags()
        profile.mailchimp_all_hash = m_add(profile.email, 'all', **clean_merge_tags)
        profile.mailchimp_tried_to_subscribe = True
        profile.update_mailchimp_fields()

        if not profile.subscription:
            m_unsubscribe(profile.mailchimp_all_hash, 'all')
        save = True

    elif profile.subscription != profile.old_subscription:

        # чувак включил подписку
        if profile.subscription is True:
            if profile.mailchimp_all_hash:
                m_resubscribe(profile.mailchimp_all_hash, 'subscribe')

        # чувак выключил подписку
        else:
            if profile.mailchimp_all_hash:
                m_unsubscribe(profile.mailchimp_all_hash, 'all')

        save = True

    if save:
        profile.old_subscription = profile.subscription
        profile.save()


@receiver(pre_delete, sender=Profile, dispatch_uid='remove_mailchimp_subscriptions')
def remove_mailchimp_subscriptions(sender, instance, using, **kwargs):
    # удаляем чувака из списков mailchimp перед удалением с сайта
    profile = instance
    if profile.mailchimp_all_hash:
        m_remove(profile.mailchimp_all_hash, 'all')


class WishListItem(models.Model):
    profile = models.ForeignKey(Profile, verbose_name='Профиль', related_name='wishlist_items', db_index=True)
    product = models.ForeignKey('catalog.Product', verbose_name='Товар', related_name='wishlist_items', db_index=True)
    option = models.ForeignKey('catalog.ProductOption', verbose_name='Вариант', related_name='wishlist_items')

    attrs = JSONField(default=dict)
    extra_products = JSONField(default=dict)
    hash = models.BigIntegerField(default=0, db_index=True)

    price_rub = models.DecimalField('Цена, руб.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    price_eur = models.DecimalField('Цена, eur.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)
    price_usd = models.DecimalField('Цена, usd.', max_digits=9, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        ordering = ['id', ]

    def __unicode__(self):
        return '{}'.format(self.id)

    @property
    def price(self):
        return currency_price(self)

    def get_price(self):
        option = self.option
        option_price_rub = option.price_rub
        option_price_eur = option.price_eur
        option_price_usd = option.price_usd

        extra_price_rub = Decimal(0.0)
        extra_price_eur = Decimal(0.0)
        extra_price_usd = Decimal(0.0)
        if self.extra_products:
            extra_products = self.product.extra_products.filter(extra_product_id__in=self.extra_products.keys())
            prices = extra_products.values('price_rub', 'price_eur', 'price_usd')
            extra_price_rub = sum([price['price_rub'] for price in prices])
            extra_price_eur = sum([price['price_eur'] for price in prices])
            extra_price_usd = sum([price['price_usd'] for price in prices])

        self.price_rub = option_price_rub + extra_price_rub
        self.price_eur = option_price_eur + extra_price_eur
        self.price_usd = option_price_usd + extra_price_usd

    def save(self, *args, **kwargs):
        self.get_price()
        return super(WishListItem, self).save(*args, **kwargs)

    def set_hash(self):
        hash = make_hash_from_cartitem(self.attrs, self.extra_products)
        self.hash = hash
        self.save()
        return hash


class Mailing(models.Model):
    email = models.EmailField(_('Email'), unique=True)
    name = models.CharField(_('Имя Фамилия'), max_length=511)
    phone = models.CharField(_('Телефон'), max_length=30, null=True, blank=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'

    def __unicode__(self):
        return '{}'.format(self.email)


@receiver(post_save, sender=Mailing)
def send_email_user(sender, instance, **kwargs):
    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        user_to = [instance.email,]
        subject = 'Вы стали участником конкурса. Ваш №{}'.format(instance.id)
        payload = {'context': instance}
        text_message = render_to_string('email/to_user/email_user_mailing.txt', payload)
        html_message = render_to_string('email/to_user/email_user_mailing.html', payload)
        msg = EmailMultiAlternatives(
                subject, text_message, from_email, user_to)
        msg.attach_alternative(html_message, 'text/html')
        msg.send()
        
    except Exception as e:
        print('При попытке отправить письмо произошла ошибка')
        print('ERROR:', e)
