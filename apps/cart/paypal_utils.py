# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __

from paypal.standard.forms import PayPalPaymentsForm

from ..utils import get_a_token


translated_strings = (_('Заказ на Bikinimini.ru'),)


def get_paypal_form(request, cart):
    amount = unicode(cart.summary_c)  # noqa
    currency = cart.currency.upper()
    order_id = unicode(cart.id)  # noqa
    approve_token = get_a_token()
    cancel_token = get_a_token()
    return_url = reverse('cart_api:paypal', kwargs={'pk': int(order_id)})

    paypal_dict = {
        'business': settings.PAYPAL_EMAIL,
        'amount': amount,
        'currency_code': currency,
        'item_name': __('Заказ на Bikinimini.ru'),
        'invoice': order_id,
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
        'return_url': request.build_absolute_uri('{}?action=return&approve_token={}'.format(return_url, approve_token)),
        'cancel_return': request.build_absolute_uri('{}?action=cancel&cancel_token={}'.format(return_url, cancel_token)),
        # 'custom': 'premium_plan',  # Custom command to correlate to some function later (optional)
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {'form': form}
    form_html = render(request, 'blocks/paypal_form.html', context).content

    return {
        'form': form,
        'form_html': form_html,
        'approve_token': approve_token,
        'cancel_token': cancel_token,
    }
