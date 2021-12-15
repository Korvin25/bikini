# -*- coding: utf-8 -*-

from apps.third_party.yookassa.domain.common import BaseObject


class ReceiptItemSupplier(BaseObject):
    """
    Class representing receipt item supplier data wrapper object

    Used in Receipt
    """
    __name = None

    __inn = None

    __phone = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = unicode(value)

    @property
    def inn(self):
        return self.__inn

    @inn.setter
    def inn(self, value):
        self.__inn = unicode(value)

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        self.__phone = unicode(value)

