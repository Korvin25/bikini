# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.request.refund_request import RefundRequest


class RefundRequestBuilder(object):
    def __init__(self):
        self.__request = RefundRequest()

    def set_payment_id(self, value):
        self.__request.payment_id = value
        return self

    def set_amount(self, value):
        self.__request.amount = value
        return self

    def set_description(self, value):
        self.__request.description = value
        return self

    def set_receipt(self, value):
        self.__request.receipt = value
        return self

    def set_sources(self, value):
        self.__request.sources = value
        return self

    def set_deal(self, value):
        self.__request.deal = value
        return self

    def build(self):
        return self.__request
