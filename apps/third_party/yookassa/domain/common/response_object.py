# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common import BaseObject
from apps.third_party.yookassa.domain.common.data_context import DataContext


class ResponseObject(BaseObject):
    """
    Base class for request objects
    """
    @staticmethod
    def context():
        return DataContext.RESPONSE
