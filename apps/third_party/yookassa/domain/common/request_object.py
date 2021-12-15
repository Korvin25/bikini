# -*- coding: utf-8 -*-

from apps.third_party.yookassa.domain.common import BaseObject
from apps.third_party.yookassa.domain.common.data_context import DataContext


class RequestObject(BaseObject):
    """
    Base class for request objects
    """
    @staticmethod
    def context():
        return DataContext.REQUEST

    def validate(self):
        """
        Validate request data
        """
        pass
