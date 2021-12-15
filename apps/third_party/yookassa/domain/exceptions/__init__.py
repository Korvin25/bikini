# -*- coding: utf-8 -*-
"""Top-level package for YooKassa API Python Client Library."""

from apps.third_party.yookassa.domain.exceptions.api_error import ApiError
from apps.third_party.yookassa.domain.exceptions.authorize_error import AuthorizeError
from apps.third_party.yookassa.domain.exceptions.bad_request_error import BadRequestError
from apps.third_party.yookassa.domain.exceptions.forbidden_error import ForbiddenError
from apps.third_party.yookassa.domain.exceptions.not_found_error import NotFoundError
from apps.third_party.yookassa.domain.exceptions.response_processing_error import ResponseProcessingError
from apps.third_party.yookassa.domain.exceptions.too_many_request_error import TooManyRequestsError
from apps.third_party.yookassa.domain.exceptions.unauthorized_error import UnauthorizedError
