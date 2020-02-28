# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def load_fixture(apps, schema_editor):
    from django.core.management import call_command
    call_command('loaddata', '20200227_product_tabs.json')


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0050_product_tabs'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
