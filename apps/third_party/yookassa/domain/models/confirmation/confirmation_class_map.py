# -*- coding: utf-8 -*-
from apps.third_party.yookassa.domain.common.confirmation_type import ConfirmationType
from apps.third_party.yookassa.domain.common.data_context import DataContext
from apps.third_party.yookassa.domain.models.confirmation.request.confirmation_embedded import \
    ConfirmationEmbedded as RequestConfirmationEmbedded
from apps.third_party.yookassa.domain.models.confirmation.request.confirmation_external import \
    ConfirmationExternal as RequestConfirmationExternal
from apps.third_party.yookassa.domain.models.confirmation.request.confirmation_qr import \
    ConfirmationQr as RequestConfirmationQr
from apps.third_party.yookassa.domain.models.confirmation.request.confirmation_redirect import \
    ConfirmationRedirect as RequestConfirmationRedirect
from apps.third_party.yookassa.domain.models.confirmation.request.confirmation_mobile_application import \
    ConfirmationMobileApplication as RequestConfirmationMobileApplication
from apps.third_party.yookassa.domain.models.confirmation.response.confirmation_embedded import \
    ConfirmationEmbedded as ResponseConfirmationEmbedded
from apps.third_party.yookassa.domain.models.confirmation.response.confirmation_external import \
    ConfirmationExternal as ResponseConfirmationExternal
from apps.third_party.yookassa.domain.models.confirmation.response.confirmation_qr import \
    ConfirmationQr as ResponseConfirmationQr
from apps.third_party.yookassa.domain.models.confirmation.response.confirmation_redirect import \
    ConfirmationRedirect as ResponseConfirmationRedirect
from apps.third_party.yookassa.domain.models.confirmation.response.confirmation_mobile_application import \
    ConfirmationMobileApplication as ResponseConfirmationMobileApplication


class ConfirmationClassMap(DataContext):
    def __init__(self):
        super(ConfirmationClassMap, self).__init__(('request', 'response'))

    @property
    def request(self):
        return {
            ConfirmationType.REDIRECT: RequestConfirmationRedirect,
            ConfirmationType.EXTERNAL: RequestConfirmationExternal,
            ConfirmationType.EMBEDDED: RequestConfirmationEmbedded,
            ConfirmationType.QR: RequestConfirmationQr,
            ConfirmationType.MOBILE_APPLICATION: RequestConfirmationMobileApplication
        }

    @property
    def response(self):
        return {
            ConfirmationType.REDIRECT: ResponseConfirmationRedirect,
            ConfirmationType.EXTERNAL: ResponseConfirmationExternal,
            ConfirmationType.EMBEDDED: ResponseConfirmationEmbedded,
            ConfirmationType.QR: ResponseConfirmationQr,
            ConfirmationType.MOBILE_APPLICATION: ResponseConfirmationMobileApplication
        }
