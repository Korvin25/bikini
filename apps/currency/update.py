# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from ..cart.models import DeliveryMethod
from ..catalog.models import (AdditionalProduct, Certificate, GiftWrapping,
                              Product, ProductOption, ProductExtraOption,
                              SpecialOfferCategory,)
from .utils import get_price_from_rub


l = logging.getLogger('currency.tasks')


def update_all_prices(currency_name, rate):
    for model in [DeliveryMethod,
                  AdditionalProduct, Certificate, GiftWrapping,
                  Product, ProductOption, ProductExtraOption,
                  SpecialOfferCategory]:

        qs = model.objects.all()
        model_name = model.__name__

        l.info('    updating {} (count={})...'.format(model_name, qs.count()))

        for obj in qs:
            price_rub = obj.price_rub
            new_price = get_price_from_rub(price_rub, rate)
            setattr(obj, 'price_{}'.format(currency_name), new_price)
            obj.save()

            if model_name not in ('Product', 'ProductOption'):
                l.info('        {} {} {}'.format(obj.id, obj.price_rub, new_price))

        l.info('    updating {}: done'.format(model_name))
