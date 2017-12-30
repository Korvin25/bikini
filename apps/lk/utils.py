# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files import File


def get_uploaded_file(url='', required=False):
    name, file = None, None
    name = url.split('/')[-1]
    # FIXME
    url = url.split('Git')[-1]

    if not name:
        if required is True:
            raise Exception('url is empty')
    else:
        try:
            file = File(open(url[1:], 'rb'))
        except IOError:
            return None, None
    return name, file


def get_error_message(e):
    try:
        err_message = unicode(e.message).decode('utf-8') or unicode(e).decode('utf-8')
    except UnicodeDecodeError:
        err_message = e.message.decode('utf-8')
    except:
        err_message = repr(e)
        # err_message = e.__class__.__name__
    return err_message
