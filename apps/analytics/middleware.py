# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from .conf import ENABLE_METRICS, SESSION_YM_CLIENT_ID_KEY, SESSION_YM_CLIENT_DT_KEY


class IsYMClientIDSetMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if ENABLE_METRICS and not (request.is_ajax() or request.path[:7] in ['/static', '/admin/', '/media/']):
            client_id = None
            if request.session:
                session_client_id = request.session.get(SESSION_YM_CLIENT_ID_KEY)
                session_client_dt = request.session.get(SESSION_YM_CLIENT_DT_KEY)

                if session_client_id and session_client_dt and (timezone.now()-session_client_dt).seconds < 3600:
                    client_id = session_client_id

            # print '---', client_id, '---'
            we_have_client_id = bool(client_id)
            request.we_need_ym_client_id = not we_have_client_id
        return None
