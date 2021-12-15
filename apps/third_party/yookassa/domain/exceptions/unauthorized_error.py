# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.exceptions.api_error import ApiError


class UnauthorizedError(ApiError):
    HTTP_CODE = 401
