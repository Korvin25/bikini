# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.generic import View

from .conf import SESSION_YM_CLIENT_ID_KEY


class SetYMClientIDView(View):

    def post(self, request, *args, **kwargs):
        client_id = request.POST.get('client_id')
        if client_id:
            request.session[SESSION_YM_CLIENT_ID_KEY] = client_id
        return JsonResponse({'result': 'ok'})
