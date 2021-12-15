# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common import BaseObject


class Confirmation(BaseObject):
    """
    Base class confirmation data objects
    """
    __type = None

    @property
    def type(self):
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = unicode(value)
