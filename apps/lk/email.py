# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives, get_connection
from django.core.urlresolvers import reverse
from django.template.loader import get_template, render_to_string
from django.utils import translation
from django.utils.translation import ugettext as _

from anymail.exceptions import AnymailError
from crequest.middleware import CrequestMiddleware

from ..settings.models import Settings


DEFAULT_SITENAME = settings.DEFAULT_SITENAME


def email_admin(subject, email_key, obj=None, settings_key='feedback_email', **kwargs):
    request = CrequestMiddleware.get_request()

    from_email = settings.DEFAULT_FROM_EMAIL
    to = (Settings.get_feedback_emails() if settings_key=='feedback_email'
          else Settings.get_orders_emails() if settings_key=='orders_email'
          else [])
    to = to or [admin[1] for admin in settings.ADMINS]

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

    # admin_backend = get_connection(settings.ADMIN_EMAIL_BACKEND)
    message = EmailMultiAlternatives(subject, text_content, from_email, to)
    message.attach_alternative(html_content, "text/html")
    # msg = message.send()
    message.send()


# def admin_send_registration_email(obj, **kwargs):
#     subject = 'Bikinimini.ru: Новая регистрация на сайте'
#     email_key = 'new_registration'
#     admin_slug = 'lk/profile'
#     email_admin(subject, email_key, obj, admin_slug=admin_slug, **kwargs)


def admin_send_order_email(obj, **kwargs):
    subject = 'Bikinimini.ru: Заказ № {}. Статус: {}'.format(obj.number, obj.show_status())
    email_key = 'order'
    admin_slug = 'cart/cart'
    email_admin(subject, email_key, obj, admin_slug=admin_slug, settings_key='orders_email', **kwargs)


def admin_send_order_error_retailcrm_email(cart, order, result, title, settings_key='feedback_email'):
    subject = title
    email_key = 'order_error_retailcrm'
    request = CrequestMiddleware.get_request()

    from_email = settings.DEFAULT_FROM_EMAIL
    to = (Settings.get_feedback_emails() if settings_key=='feedback_email'
          else Settings.get_orders_emails() if settings_key=='orders_email'
          else [])
    to = to or [admin[1] for admin in settings.ADMINS]

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
    url_retailcrm = None
    if cart.retailcrm:
        url_retailcrm = 'https://bikinimini.retailcrm.ru/orders/{}/edit'.format(cart.retailcrm)
    context = {'url_admin': 'https://bikinimini.ru/admin/cart/cart/{}/change/'.format(cart.id), 'subject': subject, 'site': site, 'order': order, 'result': result, 'url_retailcrm': url_retailcrm}
    text_content = template_text.render(context)
    html_content = template_html.render(context)

    # admin_backend = get_connection(settings.ADMIN_EMAIL_BACKEND)
    message = EmailMultiAlternatives(subject, text_content, from_email, to)
    message.attach_alternative(html_content, "text/html")
    # msg = message.send()
    message.send()
    
    
def admin_send_collback_error_retailcrm_email(item, result, title, settings_key='feedback_email'):
    subject = title
    email_key = 'collback_error_retailcrm'
    request = CrequestMiddleware.get_request()

    from_email = settings.DEFAULT_FROM_EMAIL
    to = (Settings.get_feedback_emails() if settings_key=='feedback_email'
          else Settings.get_orders_emails() if settings_key=='orders_email'
          else [])
    to = to or [admin[1] for admin in settings.ADMINS]

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

    context = {'subject': subject, 'site': site, 'order': item, 'result': result}
    text_content = template_text.render(context)
    html_content = template_html.render(context)

    # admin_backend = get_connection(settings.ADMIN_EMAIL_BACKEND)
    message = EmailMultiAlternatives(subject, text_content, from_email, to)
    message.attach_alternative(html_content, "text/html")
    # msg = message.send()
    message.send()


def admin_send_callback_order_email(obj, **kwargs):
    subject = 'Bikinimini.ru: Заказ обратного звонка'
    email_key = 'callback_order'
    admin_slug = 'feedback/callbackorder'
    email_admin(subject, email_key, obj, admin_slug=admin_slug, **kwargs)


def admin_send_blog_comment_email(obj, post, **kwargs):
    subject = 'Bikinimini.ru: Новый комментарий к посту {}'.format(post.title)
    email_key = 'blog_comment'
    admin_slug = 'blog/postcomment'
    email_admin(subject, email_key, obj, admin_slug=admin_slug, post=post, **kwargs)


def admin_send_low_in_stock_email(options, extra_products, **kwargs):
    subject = 'Bikinimini.ru: Некоторые товары заканчиваются на складе'
    email_key = 'low_in_stock'
    email_admin(subject, email_key, options=options, extra_products=extra_products, **kwargs)


def email_user_mailing(instance):
        from_email = settings.DEFAULT_FROM_EMAIL
        user_to = [instance.email,]
        subject = 'Вы стали участником конкурса. Ваш №{}'.format(instance.id)
        payload = {'context': instance}
        text_message = render_to_string('email/to_user/email_user_mailing.txt', payload)
        html_message = render_to_string('email/to_user/email_user_mailing.html', payload)
        msg = EmailMultiAlternatives(
                subject, text_message, from_email, user_to)
        msg.attach_alternative(html_message, 'text/html')
        msg.send()


def email_user(subject, email_key, profile=None, obj=None, language_to=None, mandrill=False, dummy=False, **kwargs):
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

    curr_language = translation.get_language()
    if language_to:
        translation.activate(language_to)
        subject = _(subject)

    if kwargs.get('APPEND_ORDER_NUMBER'):
        subject = '{}: {}'.format(subject, kwargs.get('APPEND_ORDER_NUMBER'))

    msg = None

    if mandrill is False:
        template_text = get_template('email/to_user/{}.txt'.format(email_key))
        template_html = get_template('email/to_user/{}.html'.format(email_key))

        context = {'profile': profile, 'subject': subject, 'site': site, 'obj': obj}
        context.update(kwargs)
        text_content = template_text.render(context)
        html_content = template_html.render(context)

        if dummy is True:
            user_backend = get_connection(settings.DUMMY_EMAIL_BACKEND)
        else:
            user_backend = get_connection(settings.EMAIL_BACKEND)

        message = EmailMultiAlternatives(subject, text_content, from_email, to)
        message.attach_alternative(html_content, "text/html")
        try:
            msg = message.send()
        except AnymailError:
            pass

        if language_to:
            translation.activate(curr_language)

        try:
            return msg[0]
        except TypeError:
            return

    else:
        user_backend = get_connection(settings.MANDRILL_EMAIL_BACKEND)

        message = EmailMessage(
            subject=subject,
            to=to,
            from_email=from_email,
            connection=user_backend,
        )
        message.template_id = kwargs.get('mandrill_template', None)
        message.merge_global_data = kwargs.get('mandrill_merge_global_data', {})
        try:
            msg = message.send()
        except AnymailError:
            pass

        if language_to:
            translation.activate(curr_language)

        try:
            return msg[0]
        except TypeError:
            return


# def send_registration_email(profile):
#     subject = 'Регистрация на сайте Bikinimini.ru'
#     email_key = 'registration'
#     email_user(subject, email_key, profile)


def send_reset_password_email(profile, signature):
    subject = 'Bikinimini.ru: Сброс пароля'
    email_key = 'reset_password'
    reset_password_link = reverse('profile_reset_password', kwargs={'signature': signature})
    email_user(subject, email_key, profile, signature=signature, reset_password_link=reset_password_link)


def send_order_email(profile, obj, **kwargs):
    subject = 'Ваш заказ на Bikinimini.ru: № %s' % unicode(obj.number)
    email_key = 'order'
    email_user(subject, email_key, profile, obj=obj, **kwargs)
