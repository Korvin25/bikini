# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.conf import settings
from django.core.urlresolvers import reverse

from apps.third_party.yookassa import Configuration, Payment
from apps.utils import absolute


Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(currency='RUB', value='200.00', description='Заказ № 000 111'):
    _return_url = reverse('cart_api:yookassa', kwargs={'pk': 111})
    payment = Payment.create({
        "amount": {
            "value": value,
            "currency": currency,
        },
        "confirmation": {
            "type": "redirect",
            "return_url": absolute(_return_url),
        },
        "capture": True,
        "description": description,
    }, uuid.uuid4())
    import ipdb; ipdb.set_trace()
    return payment
