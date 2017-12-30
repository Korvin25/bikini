# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, DetailView


class ProfileHomeView(TemplateView):
    template_name = 'profile/profile.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('home'))
        return super(ProfileHomeView, self).get(request, *args, **kwargs)
