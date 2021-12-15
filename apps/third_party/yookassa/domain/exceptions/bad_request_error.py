# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.exceptions.api_error import ApiError


class BadRequestError(ApiError):
    HTTP_CODE = 400
