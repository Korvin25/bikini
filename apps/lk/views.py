# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import login, update_session_auth_hash
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.views.generic import TemplateView, UpdateView, View

from ..cart.cart import Cart
from ..core.mixins import JSONFormMixin
from ..geo.models import Country
from .auth.utils import update_wishlist
from .forms import ProfileForm, SetPasswordForm
from .models import Profile


translated_strings = (_('Ваш пароль изменен!'),)


class ProfileMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return HttpResponseRedirect(reverse('home'))
        self.profile = request.user
        return super(ProfileMixin, self).dispatch(request, *args, **kwargs)


class ProfileHomeView(ProfileMixin, TemplateView):
    template_name = 'profile/profile.html'

    def get_context_data(self, **kwargs):
        shipping_data = {
            'country': 132,  # Россия
            'city': '',
            'postal_code': '',
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


class ProfileResetPasswordView(View):

    def get(self, request, *args, **kwargs):
        signature = kwargs.get('signature')
        user = Profile.objects.filter(signature=signature).first()
        if not user:
            # ERROR (???)
            return HttpResponseRedirect(reverse('home'))

        login(request, user)

        cart = Cart(request).cart
        cart.profile = user
        cart.save()

        update_wishlist(request, user)
        return HttpResponseRedirect(reverse('profile_set_password'))


class ProfileSetPasswordView(ProfileMixin, TemplateView):
    template_name = 'profile/set_password.html'

    def get(self, request, *args, **kwargs):
        if not self.profile.signature:
            return HttpResponseRedirect(reverse('profile'))
        return super(ProfileSetPasswordView, self).get(request, *args, **kwargs)


class ProfileFormView(ProfileMixin, JSONFormMixin, UpdateView):
    form_class = ProfileForm
    mapping = {
        'name': 'name',
        'country': 'country',
        'city': 'city',
        'postal_code': 'postal_code',
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


class ProfileSetPasswordFormView(ProfileMixin, JSONFormMixin, UpdateView):
    form_class = SetPasswordForm
    mapping = {
        'new_password': 'new_password',
        'new_password_repeat': 'new_password_repeat',
    }

    def get_success_url(self):
        return reverse('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        super(ProfileSetPasswordFormView, self).form_valid(form)
        profile = form.instance
        update_session_auth_hash(self.request, profile)

        success_message = __('Ваш пароль изменен!')
        data = {'result': 'ok', 'success_message': success_message}
        return JsonResponse(data)
