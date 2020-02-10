# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0029_add_video_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageAccordionSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_ru', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_en', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_de', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_fr', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_it', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('title_es', models.CharField(max_length=255, null=True, verbose_name='\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a')),
                ('text', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_ru', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_en', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_de', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_fr', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_it', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('text_es', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442')),
                ('order', models.IntegerField(default=10, verbose_name='\u041f\u043e\u0440\u044f\u0434\u043e\u043a')),
            ],
            options={
                'ordering': ['order', 'id'],
                'verbose_name': '\u0441\u0435\u043a\u0446\u0438\u044f',
                'verbose_name_plural': '\u0441\u0435\u043a\u0446\u0438\u0438',
            },
        ),
        migrations.AlterField(
            model_name='page',
            name='text',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_de',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_en',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_es',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_fr',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_it',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AlterField(
            model_name='page',
            name='text_ru',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='\u0422\u0435\u043a\u0441\u0442'),
        ),
        migrations.AddField(
            model_name='pageaccordionsection',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accordion_sections', to='content.Page', verbose_name='\u0421\u0442\u0440\u0430\u043d\u0438\u0446\u0430'),
        ),
    ]
