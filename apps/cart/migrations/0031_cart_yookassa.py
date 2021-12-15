# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0030_paymentmethod_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='yoo_id',
            field=models.UUIDField(blank=True, null=True, verbose_name='ID \u043f\u043b\u0430\u0442\u0435\u0436\u0430'),
        ),
        migrations.AddField(
            model_name='cart',
            name='yoo_paid',
            field=models.NullBooleanField(default=None, verbose_name='\u041e\u043f\u043b\u0430\u0447\u0435\u043d?'),
        ),
        migrations.AddField(
            model_name='cart',
            name='yoo_return_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL \u0434\u043b\u044f \u043f\u0435\u0440\u0435\u043d\u0430\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u044f'),
        ),
        migrations.AddField(
            model_name='cart',
            name='yoo_status',
            field=models.CharField(blank=True, default='', max_length=15, verbose_name='\u0421\u0442\u0430\u0442\u0443\u0441 \u043f\u043b\u0430\u0442\u0435\u0436\u0430'),
        ),
        migrations.AddField(
            model_name='cart',
            name='yoo_test',
            field=models.NullBooleanField(default=None, verbose_name='\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439 \u043f\u043b\u0430\u0442\u0435\u0436?'),
        ),
    ]
