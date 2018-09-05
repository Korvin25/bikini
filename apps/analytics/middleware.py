# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.deprecation import MiddlewareMixin

from .conf import ENABLE_METRICS, SESSION_YM_CLIENT_ID_KEY


class IsYMClientIDSetMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if ENABLE_METRICS and not (request.is_ajax() or request.path[:7] in ['/static', '/admin/', '/media/']):
            client_id = (request.user.ym_client_id or request.session.get(SESSION_YM_CLIENT_ID_KEY)
                         if request.user.is_authenticated()
                         else request.session.get(SESSION_YM_CLIENT_ID_KEY) if request.session
                         else None)
            we_have_client_id = bool(client_id)
            request.we_need_ym_client_id = not we_have_client_id
        return None
