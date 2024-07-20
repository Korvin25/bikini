# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import hashlib
from urlparse import urlparse
from urllib import urlencode


def calculate_signature(*args):
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def parse_response(request):
    """
    :param request: Link.
    :return: Dictionary.
    """
    params = {}

    for item in urlparse(request).query.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params


def check_signature_result(
    order_number,  # invoice number
    received_sum,  # cost of goods, RU
    received_signature,  # SignatureValue
    password  # Merchant password
):
    signature = calculate_signature(received_sum, order_number, password)
    if signature.lower() == received_signature.lower():
        return True
    return False


# Формирование URL переадресации пользователя на оплату.

def generate_payment_link(
    merchant_login,  # Merchant login
    merchant_password_1,  # Merchant password
    cost,  # Cost of goods, RU
    number,  # Invoice number
    description,  # Description of the purchase
    email,
    currency,
    receipt,
    is_test = 0,
    robokassa_payment_url = 'https://auth.robokassa.ru/Merchant/Index.aspx',
):
    """URL for redirection of the customer to the service.
    """
    if currency != 'RUB':
        signature = calculate_signature(
            merchant_login,
            cost,
            number,
            currency,
            receipt,
            merchant_password_1
        )

        data = {
            'MerchantLogin': merchant_login,
            'OutSum': cost,
            'InvId': number,
            'Description': description,
            'SignatureValue': signature,
            'Email': email,
            'IsTest': is_test,
            'OutSumCurrency': currency,
            'Receipt': receipt
        }
    else:
        signature = calculate_signature(
            merchant_login,
            cost,
            number,
            receipt,
            merchant_password_1
        )

        data = {
            'MerchantLogin': merchant_login,
            'OutSum': cost,
            'InvId': number,
            'Description': description,
            'SignatureValue': signature,
            'Email': email,
            'IsTest': is_test,
            'Receipt': receipt
        }
    return '{}?{}'.format(robokassa_payment_url, urlencode(data))


# Получение уведомления об исполнении операции (ResultURL).

def result_payment(merchant_password_2, request):
    """Verification of notification (ResultURL).
    :param request: HTTP parameters.
    """
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']


    if check_signature_result(number, cost, signature, merchant_password_2):
        return 'OK{}'.format(param_request["InvId"]), signature
    return "bad sign", ""


# Проверка параметров в скрипте завершения операции (SuccessURL).

def check_success_payment(merchant_password_1, request):
    """ Verification of operation parameters ("cashier check") in SuccessURL script.
    :param request: HTTP parameters
    """
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']


    if check_signature_result(number, cost, signature, merchant_password_1):
        return "Thank you for using our service"
    return "bad sign"
