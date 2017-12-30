# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect, Http404, HttpResponseForbidden
from django.views.generic import View, FormView, CreateView, RedirectView

from apps.cart.cart import Cart
from apps.core.mixins import JSONFormMixin
from apps.lk.email import admin_send_registration_email, send_registration_email
from apps.lk.models import Profile
from apps.lk.utils import get_error_message
from .forms import LoginForm, RegistrationForm


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

        data = {'result': 'ok', 'popup': '#step3', 'profile_shipping_data': profile.shipping_data}
        return JsonResponse(data)


# class ResetPasswordView(FormView):
#     """
#     Обновляем пароль и отправляем юзеру
#     """
#     form_class = ResetPasswordForm

#     def form_invalid(self, form):
#         errors = []
#         for k in form.errors:
#             errors.append({'name': k, 'error_message': form.errors[k][0]})
#         return JsonResponse({'errors': errors}, status=400)

#     def form_valid(self, form):
#         email = form.cleaned_data.get('email')
#         user = Profile.objects.get(email=email)

#         user.reset_pass()
#         response = {'result': 'ok'}
#         return JsonResponse({'response': response})
