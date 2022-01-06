# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0039_cart_nullable_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliverymethod',
            name='languages',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('ru', 'RU'), ('en', 'EN'), ('de', 'DE'), ('fr', 'FR'), ('it', 'IT'), ('es', 'ES')], default=['ru', 'en', 'de', 'fr', 'it', 'es'], max_length=255, null=True, verbose_name='\u042f\u0437\u044b\u043a\u043e\u0432\u044b\u0435 \u0440\u0430\u0437\u0434\u0435\u043b\u044b'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='languages',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('ru', 'RU'), ('en', 'EN'), ('de', 'DE'), ('fr', 'FR'), ('it', 'IT'), ('es', 'ES')], default=['ru', 'en', 'de', 'fr', 'it', 'es'], max_length=255, null=True, verbose_name='\u042f\u0437\u044b\u043a\u043e\u0432\u044b\u0435 \u0440\u0430\u0437\u0434\u0435\u043b\u044b'),
        ),
    ]
