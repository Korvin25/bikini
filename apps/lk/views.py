# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import update_session_auth_hash
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import TemplateView, UpdateView

from ..core.mixins import JSONFormMixin
from ..geo.models import Country
from .forms import ProfileForm


class ProfileMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('home'))
        return super(ProfileMixin, self).dispatch(request, *args, **kwargs)


class ProfileHomeView(ProfileMixin, TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        shipping_data = {
            'country': 132,  # Россия
            'city': '',
            'address': '',
            'phone': '',
            'name': '',
        }
        profile = self.request.user
        if profile.is_authenticated():
            shipping_data.update(profile.shipping_data)

        context = {
            'countries': Country.objects.values('id', 'title'),
            'shipping_data': shipping_data,
        }
        context.update(super(ProfileHomeView, self).get_context_data(**kwargs))
        return context


class ProfileFormView(ProfileMixin, JSONFormMixin, UpdateView):
    form_class = ProfileForm
    mapping = {
        'name': 'name',
        'country': 'country',
        'city': 'city',
        'address': 'address',
        'phone': 'phone',
        'email': 'email',
        'old_password': 'old_password',
        'new_password': 'new_password',
    }

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        super(ProfileFormView, self).form_valid(form)
        profile = form.instance
        update_session_auth_hash(self.request, profile)
        data = {'result': 'ok', 'has_password': profile.has_password}
        return JsonResponse(data)
