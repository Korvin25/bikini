# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common.type_factory import TypeFactory
from apps.third_party.yookassa.domain.models.payment_data.payment_data_class_map import PaymentDataClassMap


class PaymentDataFactory(TypeFactory):
    """
    Factory for payment data objects
    """

    def __init__(self):
        super(PaymentDataFactory, self).__init__(PaymentDataClassMap())
