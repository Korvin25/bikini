# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ipn', '0008_auto_20181128_1032'),
        ('cart', '0036_cart_paypal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='paypal_id',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='paypal_redirect_url',
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_ipn_obj',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ipn.PayPalIPN'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_txn_id',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='PayPal: ID \u0442\u0440\u0430\u043d\u0437\u0430\u043a\u0446\u0438\u0438'),
        ),
        migrations.AddField(
            model_name='cart',
            name='paypal_txn_type',
            field=models.CharField(blank=True, max_length=31, null=True, verbose_name='PayPal: \u0422\u0438\u043f \u0442\u0440\u0430\u043d\u0437\u0430\u043a\u0446\u0438\u0438'),
        ),
        migrations.AlterField(
            model_name='cart',
            name='paypal_status',
            field=models.CharField(blank=True, choices=[('active', '\u0430\u043a\u0442\u0438\u0432\u0435\u043d'), ('created', '\u0441\u043e\u0437\u0434\u0430\u043d'), ('pending', '\u0432 \u043e\u0436\u0438\u0434\u0430\u043d\u0438\u0438'), ('processed', '\u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d'), ('in-progress', '\u0432 \u0445\u043e\u0434\u0435 \u0432\u044b\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f'), ('completed', '\u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d'), ('paid', '\u043e\u043f\u043b\u0430\u0447\u0435\u043d'), ('cancelled', '\u043e\u0442\u043c\u0435\u043d\u0435\u043d'), ('denied', '\u043e\u0442\u043a\u0430\u0437\u0430\u043d\u043e'), ('refused', '\u043e\u0442\u043a\u0430\u0437\u0430\u043d\u043e'), ('declined', '\u043e\u0442\u043a\u043b\u043e\u043d\u0435\u043d'), ('cleared', '\u0443\u0434\u0430\u043b\u0435\u043d'), ('failed', '\u043d\u0435 \u0443\u0434\u0430\u043b\u0441\u044f'), ('expired', '\u0438\u0441\u0442\u0435\u043a'), ('refunded', '\u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0435\u043d'), ('partially_refunded', '\u0447\u0430\u0441\u0442\u0438\u0447\u043d\u043e \u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0435\u043d'), ('reversed', '\u043e\u0431\u0440\u0430\u0442\u043d\u044b\u0439'), ('canceled_reversal', '\u043e\u0442\u043c\u0435\u043d\u0435\u043d\u043d\u044b\u0439 \u043e\u0431\u0440\u0430\u0442\u043d\u044b\u0439'), ('rewarded', '\u043d\u0430\u0433\u0440\u0430\u0436\u0434\u0435\u043d'), ('unclaimed', '\u043d\u0435\u0432\u043e\u0441\u0442\u0440\u0435\u0431\u043e\u0432\u0430\u043d'), ('uncleared', '\u043d\u0435\u043e\u0447\u0438\u0449\u0435\u043d'), ('voided', '\u0430\u043d\u043d\u0443\u043b\u0438\u0440\u043e\u0432\u0430\u043d'), ('error', '\u043e\u0448\u0438\u0431\u043a\u0430')], default='', max_length=15, null=True, verbose_name='PayPal: \u0421\u0442\u0430\u0442\u0443\u0441 \u043f\u043b\u0430\u0442\u0435\u0436\u0430'),
        ),
    ]
