# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from ..third_party.yookassa import Payment


def get_payment(cart):
    # запрашиваем данные о платеже (и обновляем его в случае необходимости)
    try:
        _id = str(cart.yoo_id)
        payment = Payment.find_one(_id)
        return payment
    except Exception:
        pass


def update_cart_with_payment(cart, payment=None, force=False, logger=None):
    if payment is None:
        payment = get_payment(cart)
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

        if logger: logger.info('  (cart id {} / payment {}) done! new status: {}'.format(cart.id, payment.id, cart.yoo_status))
        return cart.yoo_status
