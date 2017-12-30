# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.template import Context
from django.template.loader import get_template

from crequest.middleware import CrequestMiddleware

from ..settings.models import Setting


DEFAULT_SITENAME = settings.DEFAULT_SITENAME


def email_admin(subject, email_key, obj=None, settings_key='feedback_email', **kwargs):
    request = CrequestMiddleware.get_request()

    from_email = settings.DEFAULT_FROM_EMAIL
    try:
        to = [s.strip() for s in Setting.objects.get(key=settings_key).value.split('\r\n')]
    except Setting.DoesNotExist:
        to = [settings.ADMINS[0][1]]

    site = ''
    try:
        site = request.get_host()
    except AttributeError:
        site = DEFAULT_SITENAME
    else:
        if not site:
            site = DEFAULT_SITENAME

    template_text = get_template('email/to_admin/{}.txt'.format(email_key))
    template_html = get_template('email/to_admin/{}.html'.format(email_key))

    context = {'obj': obj, 'subject': subject, 'site': site}
    context.update(kwargs)
    text_content = template_text.render(context)
    html_content = template_html.render(context)

    message = EmailMultiAlternatives(subject, text_content, from_email, to)
    message.attach_alternative(html_content, "text/html")
    msg = message.send()
    # try:
    #     msg = message.send()
    # except AnymailError:
    #     pass


def admin_send_registration_email(obj):
    subject = 'Bikinimini.ru: Новая регистрация на сайте'
    email_key = 'new_registration'
    admin_slug = 'lk/profile'
    email_admin(subject, email_key, obj, admin_slug=admin_slug)


def email_user(subject, email_key, profile, obj=None, **kwargs):
    request = CrequestMiddleware.get_request()

    from_email = settings.DEFAULT_FROM_EMAIL
    to = [profile.email]

    site = ''
    try:
        site = request.get_host()
    except AttributeError:
        site = DEFAULT_SITENAME
    else:
        if not site:
            site = DEFAULT_SITENAME

    template_text = get_template('email/to_user/{0}.txt'.format(email_key))
    template_html = get_template('email/to_user/{0}.html'.format(email_key))

    context = {'profile': profile, 'subject': subject, 'site': site, 'obj': obj}
    context.update(kwargs)
    text_content = template_text.render(context)
    html_content = template_html.render(context)

    message = EmailMultiAlternatives(subject, text_content, from_email, to)
    message.attach_alternative(html_content, "text/html")
    msg = message.send()

    try:
        return msg[0]
    except TypeError:
        return


def send_registration_email(profile):
    subject = 'Регистрация на сайте Bikinimini.ru'
    email_key = 'registration'
    email_user(subject, email_key, profile)


def send_reset_password_email(profile, passwd):
    subject = 'Bikinimini.ru: Сброс пароля'
    email_key = 'reset_password'
    profile_kwargs = {'passwd': passwd}
    email_user(subject, email_key, profile, **profile_kwargs)
