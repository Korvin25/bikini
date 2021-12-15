# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.models.confirmation.confirmation import Confirmation


class ConfirmationRequest(Confirmation):
    """
    Base class confirmation request data objects
    """
    __locale = None

    @property
    def locale(self):
        return self.__locale

    @locale.setter
    def locale(self, value):
        self.__locale = unicode(value)
