# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as __
from django.views.generic import View, FormView, CreateView, RedirectView

from apps.cart.cart import Cart
from apps.core.mixins import JSONFormMixin
from apps.lk.email import send_reset_password_email
from apps.lk.models import Profile, WishListItem
from apps.lk.utils import get_error_message
from .forms import LoginForm, RegistrationForm, ResetPasswordForm
from .utils import update_wishlist


translated_strings = (_('На ваш email отправлены дальнейшие инструкции по сбросу пароля'),)


class LogoutView(View):
    """
    Разлогиниваем юзера и перебрасываем на главную
    """
    def get(self, request, *args, **kwargs):
        profile = request.user
        logout(request)
        return HttpResponseRedirect(redirect_to=reverse('home'))


class LoginView(JSONFormMixin, FormView):
    """
    Логин
    """
    form_class = LoginForm
    mapping = {
        'email': 'email',
        'password': 'password',
    }

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)

        user = authenticate(**form.cleaned_data)
        if user:
            login(self.request, user)

        cart = Cart(self.request).cart
        cart.profile = user
        cart.save()

        update_wishlist(self.request, user)
        data = {'result': 'ok', 'popup': '#step3', 'profile_shipping_data': user.shipping_data}
        return JsonResponse(data)


class RegistrationView(JSONFormMixin, CreateView):
    """
    Регистрация
    """
    profile_type = ''
    form_class = RegistrationForm
    model = Profile
    mapping = {
        'email': 'email',
        'password': 'password',
        'name': 'name',
    }

    def get_success_url(self):
        return reverse('home')

    def get_form(self, *args, **kwargs):
        form = self.form_class(self.POST)
        return form

    def form_valid(self, form):
        super(RegistrationView, self).form_valid(form)
        profile = form.instance

        profile.backend = 'django.contrib.auth.backends.ModelBackend'
        login(self.request, profile)

        cart = Cart(self.request).cart
        cart.profile = profile
        cart.save()

        # profile.get_signature()
        # send_registration_email(profile)
        # admin_send_registration_email(profile)

        update_wishlist(self.request, profile)
        data = {'result': 'ok', 'popup': '#step3', 'profile_shipping_data': profile.shipping_data}
        return JsonResponse(data)


class ResetPasswordView(JSONFormMixin, FormView):
    """
    Сброс пароля
    """
    form_class = ResetPasswordForm
    mapping = {
        'email': 'email',
    }

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        profile = Profile.objects.get(email__iexact=email)

        signature = profile.get_signature()
        send_reset_password_email(profile, signature)

        success_message = __('На ваш email отправлены дальнейшие инструкции по сбросу пароля')
        data = {'result': 'ok', 'success_message': success_message}
        return JsonResponse(data)
