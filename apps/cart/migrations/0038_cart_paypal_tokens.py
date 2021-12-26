# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0037_cart_paypal'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='paypal_approve_token',
            field=models.CharField(blank=True, default='', max_length=31, verbose_name='PayPal: \u0422\u043e\u043a\u0435\u043d \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_cancel_token',
            field=models.CharField(blank=True, default='', max_length=31, verbose_name='PayPal: \u0422\u043e\u043a\u0435\u043d \u043e\u0442\u043c\u0435\u043d\u044b'),
        ),
    ]
