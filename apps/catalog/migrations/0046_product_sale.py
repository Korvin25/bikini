# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0045_update_specialoffer_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_on_sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='sale_percent',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u0421\u043a\u0438\u0434\u043a\u0430, %'),
        ),
        migrations.AddField(
            model_name='product',
            name='sale_price_eur',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='\u0426\u0435\u043d\u0430 \u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439, eur.'),
        ),
        migrations.AddField(
            model_name='product',
            name='sale_price_rub',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='\u0426\u0435\u043d\u0430 \u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439, \u0440\u0443\u0431.'),
        ),
        migrations.AddField(
            model_name='product',
            name='sale_price_usd',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True, verbose_name='\u0426\u0435\u043d\u0430 \u0441\u043e \u0441\u043a\u0438\u0434\u043a\u043e\u0439, usd.'),
        ),
        migrations.AddField(
            model_name='product',
            name='show_only_on_sale',
            field=models.BooleanField(default=False, verbose_name='\u041e\u0442\u043e\u0431\u0440\u0430\u0436\u0430\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u0432 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438 SALE'),
        ),
    ]
