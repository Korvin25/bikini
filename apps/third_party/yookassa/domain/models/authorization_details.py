# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common import BaseObject


class AuthorizationDetails(BaseObject):
    """
       Class representing authorization details data wrapper object
       """
    __rrn = None

    __auth_code = None

    @property
    def rrn(self):
        return self.__rrn

    @rrn.setter
    def rrn(self, value):
        self.__rrn = unicode(value)

    @property
    def auth_code(self):
        return self.__auth_code

    @auth_code.setter
    def auth_code(self, value):
        self.__auth_code = unicode(value)
