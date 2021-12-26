# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random
import string

from django.conf import settings
from django.contrib.admin.utils import quote
from django.core.urlresolvers import reverse
from django.utils import timezone

from crequest.middleware import CrequestMiddleware


DEFAULT_SCHEME = settings.DEFAULT_SCHEME
DEFAULT_SITENAME = settings.DEFAULT_SITENAME
MEDIA_URL = settings.MEDIA_URL

ASCII_CHARS = string.ascii_letters
DIGITS_CHARS = string.digits
TOKEN_CHARS = ASCII_CHARS + '-' + DIGITS_CHARS


def absolute(url=None, append_media_url=False):
    media_url = MEDIA_URL if append_media_url else ''
    if url and not url.startswith('http'):
        url = '{}://{}{}{}'.format(DEFAULT_SCHEME, DEFAULT_SITENAME, media_url, url) if url else None
    return url


def get_current_request():
    return CrequestMiddleware.get_request()


def get_current_user(request=None):
    request = request or get_current_request()
    return request.user if (request and request.user.is_authenticated()) else None


def get_current_timezone():
    return timezone.get_current_timezone()


def get_site_url():
    request = get_current_request()
    site = ''
    try:
        site = '{}://{}'.format(request.scheme, request.get_host())
    except AttributeError:
        site = '{}://{}'.format(DEFAULT_SCHEME, DEFAULT_SITENAME)
    else:
        if not site:
            site = '{}://{}'.format(DEFAULT_SCHEME, DEFAULT_SITENAME)
    return site


def get_admin_url(obj):
    # FROM: django.contrib.admin.views.main.Changelist.url_for_result()
    opts = obj.__class__._meta
    try:
        return absolute(reverse('admin:%s_%s_change' % (opts.app_label, opts.model_name),
                                args=(quote(obj.pk),)))
    except Exception:
        return ''


def get_absolute_url(obj):
    try:
        return absolute(obj.get_absolute_url())
    except Exception:
        return ''


def get_error_message(e):
    try:
        err_message = unicode(e.message).decode('utf-8') or unicode(e).decode('utf-8')  # noqa
    except (UnicodeDecodeError, UnicodeEncodeError) as err:  # noqa
        err_message = unicode(e.message)  # noqa
    except Exception:
        err_message = repr(e)
        # err_message = e.__class__.__name__
    if err_message.startswith("'ascii' codec"):
        err_message = 'Unknown error'
    return err_message


def get_a_token(length=20, charset=None):
    CHARS = {
        'ascii': ASCII_CHARS,
        'digits': DIGITS_CHARS,
    }.get(charset, TOKEN_CHARS)
    return ''.join([random.choice(CHARS) for x in range(length)])
