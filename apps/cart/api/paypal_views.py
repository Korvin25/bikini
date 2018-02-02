# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render

from paypal.standard.forms import PayPalPaymentsForm


def paypal_form(request):
    paypal_dict = {
        # "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": "10000000.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": "https://www.example.com" + reverse('paypal-ipn'),
        "return_url": "https://www.example.com/your-return-location/",
        "cancel_return": "https://www.example.com/your-cancel-location/",

        'business': settings.PAYPAL_EMAIL,
        # 'amount': '1',
        # # 'currency_code': 'RUB',
        # 'currency_code': 'USD',
        # 'item_name': 'Заказ на Bikinimini.ru',
        # 'invoice': '55',
        # 'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        # 'return_url': request.build_absolute_uri('{}?return'.format(reverse('profile'))),
        # 'cancel_return': request.build_absolute_uri('{}?cancel'.format(reverse('profile'))),
        # # 'custom': 'premium_plan',  # Custom command to correlate to some function later (optional)
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    return render(request, 'blocks/paypal_form.html', context)
