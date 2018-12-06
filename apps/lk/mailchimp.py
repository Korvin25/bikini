# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import traceback

from django.conf import settings

from mailchimp3 import MailChimp


logger_errors = logging.getLogger('mailchimp.errors')


MAILCHIMP_ENABLED = settings.MAILCHIMP_ENABLED
client = (MailChimp(mc_api=settings.MAILCHIMP_API_KEY, mc_user=settings.MAILCHIMP_USERNAME) if MAILCHIMP_ENABLED
          else None)


def get_list_id(list_type='all'):
    # if list_type not in ['all', 'subscribe', 'unsubscribe']:
    if list_type not in ['all']:
        list_type = 'all'
    list_id = settings.MAILCHIMP_LIST_IDS[list_type]
    return list_id


def get_list(list_type='all'):
    list_id = get_list_id(list_type)
    return client.lists.get(list_id)


def get_list_name(list_type='all'):
    list = get_list(list_type)
    return list['name']


def m_add(email, list_type='all', **kwargs):
    if not MAILCHIMP_ENABLED: return None

    try:
        list_id = get_list_id(list_type)
        add_kwargs = {'email_address': email, 'status': 'subscribed'}
        if kwargs:
            add_kwargs['merge_fields'] = kwargs
        m = client.lists.members.create(list_id, add_kwargs)
        return m['id']
    except Exception as e:
        try:
            logger_errors.error('----------')
            logger_errors.error('Ошибка в m_add(): {}: {}'.format(repr(type(e)).decode('utf-8'), e.message.decode('utf-8')))
            logger_errors.error('* email: "{}"'.format(email))
            logger_errors.error('* list_type: "{}"'.format(list_type))
            for k, v in kwargs.iteritems():
                logger_errors.error('* {}: "{}"'.format(k, v))
        except AttributeError:
            pass
        else:
            try:
                logger_errors.info('\n---\n{}---'.format(traceback.format_exc()))
            except UnicodeDecodeError:
                pass
        return None


def m_update_fields(hash, list_type='all', **kwargs):
    if not MAILCHIMP_ENABLED: return None
    print hash, list_type, kwargs

    try:
        list_id = get_list_id(list_type)
        client.lists.members.update(list_id, hash, {'merge_fields': kwargs})
        return True
    except Exception as e:
        try:
            logger_errors.error('----------')
            logger_errors.error('Ошибка в m_update_fields(): {}: {}'.format(repr(type(e)).decode('utf-8'), e.message.decode('utf-8')))
            logger_errors.error('* hash: "{}"'.format(hash))
            logger_errors.error('* list_type: "{}"'.format(list_type))
            for k, v in kwargs.iteritems():
                logger_errors.error('* {}: "{}"'.format(k, v))
        except AttributeError:
            pass
        else:
            try:
                logger_errors.info('\n---\n{}---'.format(traceback.format_exc()))
            except UnicodeDecodeError:
                pass
        return None


def m_resubscribe(hash, list_type='all'):
    if not MAILCHIMP_ENABLED: return None

    try:
        list_id = get_list_id(list_type)
        client.lists.members.update(list_id, hash, {'status': 'subscribed'})
        return True
    except Exception as e:
        try:
            logger_errors.error('----------')
            logger_errors.error('Ошибка в m_resubscribe(): {}: {}'.format(repr(type(e)).decode('utf-8'), e.message.decode('utf-8')))
            logger_errors.error('* hash: "{}"'.format(hash))
            logger_errors.error('* list_type: "{}"'.format(list_type))
        except AttributeError:
            pass
        else:
            try:
                logger_errors.info('\n---\n{}---'.format(traceback.format_exc()))
            except UnicodeDecodeError:
                pass
        return None


def m_unsubscribe(hash, list_type='all'):
    if not MAILCHIMP_ENABLED: return None

    try:
        list_id = get_list_id(list_type)
        client.lists.members.update(list_id, hash, {'status': 'unsubscribed'})
        return True
    except Exception as e:
        try:
            logger_errors.error('----------')
            logger_errors.error('Ошибка в m_unsubscribe(): {}: {}'.format(repr(type(e)).decode('utf-8'), e.message.decode('utf-8')))
            logger_errors.error('* hash: "{}"'.format(hash))
            logger_errors.error('* list_type: "{}"'.format(list_type))
        except AttributeError:
            pass
        else:
            try:
                logger_errors.info('\n---\n{}---'.format(traceback.format_exc()))
            except UnicodeDecodeError:
                pass
        return None


def m_remove(hash, list_type='all'):
    if not MAILCHIMP_ENABLED: return None

    try:
        list_id = get_list_id(list_type)
        client.lists.members.delete(list_id, hash)
        return True
    except Exception as e:
        try:
            logger_errors.error('----------')
            logger_errors.error('Ошибка в m_remove(): {}: {}'.format(repr(type(e)).decode('utf-8'), e.message.decode('utf-8')))
            logger_errors.error('* hash: "{}"'.format(hash))
            logger_errors.error('* list_type: "{}"'.format(list_type))
        except AttributeError:
            pass
        else:
            try:
                logger_errors.info('\n---\n{}---'.format(traceback.format_exc()))
            except UnicodeDecodeError:
                pass
        return None
