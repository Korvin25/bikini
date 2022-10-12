# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import json

from django.utils import timezone
from django.conf import settings

from ..third_party.yookassa import Payment as YooPayment


def yoo_get_payment(cart):
    # запрашиваем данные о платеже (и обновляем его в случае необходимости)
    try:
        _id = str(cart.yoo_id)
        payment = YooPayment.find_one(_id)
        return payment
    except Exception:
        pass


def life_pay_post(cart, logger):
    try:
        # -- Удаленная фискализация --
        res = cart.life_pay_post_request()
        if res['code'] == 0:
            cart.life_pay_id = res['data']['uuid']
            cart.save()
        if logger: logger.info('  (cart id {}) updating cart... Удаленная фискализация: {}'.format(cart.id, res))
    except Exception as e:
        if logger: logger.info('  (cart id {}) updating cart... Удаленная фискализация: {}'.format(cart.id, e))


def yoo_update_cart_with_payment(cart, payment=None, force=False, logger=None):
    if payment is None:
        payment = yoo_get_payment(cart)
        if not payment and logger: logger.warning('  (cart id {}) no payment found!'.format(cart.id))

    if payment and (cart.yoo_status == 'pending' or force is True):

        if logger: logger.info('  (cart id {} / payment {}) updating cart...'.format(cart.id, payment.id))

        # обновляем cart
        for key in ['status', 'paid']:
            setattr(cart, 'yoo_{}'.format(key), getattr(payment, key))
        cart.save()

        # если заказ оплачен, делаем всякие штуки
        if cart.yoo_paid is True:
            cart.payment_date = timezone.now()
            cart.save()
            # -- отправка имейлов --
            cart.send_order_emails()
            # -- остатки на складе --
            cart.update_in_stock()
            # -- Удаленная фискализация --
            life_pay_post(cart, logger)
        else:
            cart.send_order_emails()

        if logger: logger.info('  (cart id {} / payment {}) done! new status: {}'.format(cart.id, payment.id, cart.yoo_status))
        return cart.yoo_status
