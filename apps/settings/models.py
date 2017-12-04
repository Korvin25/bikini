# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from tinymce.models import HTMLField


class Setting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    value = models.TextField('Значение', null=True, blank=True)
    description = models.TextField('Описание')

    class Meta:
        ordering = ['key', ]
        verbose_name = 'настройка'
        verbose_name_plural = 'текстовые настройки'

    def __unicode__(self):
        return self.description


class VisualSetting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    value = RichTextField('Значение', null=True, blank=True)
    # value = RichTextUploadingField('Значение', null=True, blank=True)
    # value = HTMLField('Значение', null=True, blank=True)
    description = models.TextField('Описание')

    class Meta:
        ordering = ['key', ]
        verbose_name = 'текстовая настройка (wysiwyg)'
        verbose_name_plural = 'текстовые настройки (wysiwyg)'

    def __unicode__(self):
        return self.description


class SEOSetting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    description = models.CharField('Страница', max_length=255)
    title = models.CharField(
        'Meta title',
        max_length=255, null=True, blank=True,
        help_text='Оставьте пустым, чтобы использовать название страницы (выше)',
    )
    meta_desc = models.TextField(
        'Meta description',
        max_length=255, null=True, blank=True,
        help_text='Оставьте пустым, чтобы использовать название страницы (выше)',
    )
    meta_keyw = models.TextField(
        'Meta keywords (через запятую)',
        max_length=255, null=True, blank=True,
        help_text='Оставьте пустым, чтобы использовать название страницы (выше)',
    )
    seo_text = RichTextField('SEO-текст', blank=True)
    # seo_text = RichTextUploadingField('SEO-текст', blank=True)
    # seo_text = HTMLField('SEO-текст', blank=True)

    class Meta:
        ordering = ['key', ]
        verbose_name = 'SEO-настройка'
        verbose_name_plural = 'SEO-настройки'

    def __unicode__(self):
        return self.key

    def get_meta_title(self):
        return self.title if self.title else '{} — Bikinimini.ru'.format(self.description)

    def get_meta_desc(self):
        return self.meta_desc if self.meta_desc else self.description

    def get_meta_keyw(self):
        return self.meta_keyw if self.meta_keyw else SEOSetting.objects.get(key='global').meta_keyw

    def show_meta_title(self):
        return self.title if self.title else ''
    show_meta_title.allow_tags = True
    show_meta_title.short_description = 'Meta title'

    def show_meta_desc(self):
        return self.meta_desc if self.meta_desc else ''
    show_meta_desc.allow_tags = True
    show_meta_desc.short_description = 'Meta description'

    def show_meta_keyw(self):
        return self.meta_keyw if self.meta_keyw else ''
    show_meta_keyw.allow_tags = True
    show_meta_keyw.short_description = 'Meta keywords'

    def has_seo_text(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.seo_text 
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'


class MetatagModel(models.Model):
    meta_title = models.CharField(
        'Meta title',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать поле "Заголовок"',
    )
    meta_desc = models.CharField(
        'Meta description',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать поле "Заголовок"',
    )
    meta_keyw = models.CharField(
        'Meta keywords (через запятую)',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать поле "Заголовок"',
    )
    seo_text = RichTextField('SEO-текст', blank=True)
    # seo_text = HTMLField('SEO-текст', blank=True)

    class Meta:
        abstract = True

    def get_title(self):
        return self.title

    def get_meta_title(self):
        return self.meta_title if self.meta_title else '{} — Bikinimini.ru'.format(self.get_title())

    def get_meta_desc(self):
        return self.meta_desc if self.meta_desc else self.get_title()

    def get_meta_keyw(self):
        return self.meta_keyw if self.meta_keyw else SEOSetting.objects.get(key='global').meta_keyw

    def has_seo_text(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.seo_text 
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'
