# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common.type_factory import TypeFactory
from apps.third_party.yookassa.domain.models.payout_data.payout_destination_class_map import PayoutDestinationClassMap


class PayoutDestinationFactory(TypeFactory):
    """
    Factory for payment data objects
    """

    def __init__(self):
        super(PayoutDestinationFactory, self).__init__(PayoutDestinationClassMap())
