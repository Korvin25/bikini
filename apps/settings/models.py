# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField

from ..core.regions_utils import region_field


class Setting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    value = models.TextField('Значение', null=True, blank=True)
    description = models.TextField('Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key', ]
        verbose_name = 'настройка'
        verbose_name_plural = 'текстовые настройки'

    def __unicode__(self):
        return self.description

    @classmethod
    def get_seo_title_suffix(cls):
        DEFAULT_PREFIX = 'Bikinimini.ru'
        setting = cls.objects.filter(key='title_suffix').first()
        title_suffix = setting.value if setting else DEFAULT_PREFIX
        return title_suffix or DEFAULT_PREFIX


class VisualSetting(models.Model):
    key = models.SlugField('Код', max_length=255, unique=True)
    value = RichTextUploadingField('Значение', null=True, blank=True)
    description = models.TextField('Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    h1 = models.CharField(
        'H1 (на страницах, где он предусмотрен)',
        max_length=255, null=True, blank=True,
        help_text='Оставьте пустым, чтобы использовать название страницы (выше)',
    )
    seo_text = RichTextUploadingField('SEO-текст', blank=True)

    title_spb = models.CharField('Meta title (Санкт-Петербург)', max_length=255, null=True, blank=True)
    title_nsk = models.CharField('Meta title (Новосибирск)', max_length=255, null=True, blank=True)
    title_sam = models.CharField('Meta title (Самара)', max_length=255, null=True, blank=True)
    meta_desc_spb = models.TextField('Meta description (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_desc_nsk = models.TextField('Meta description (Новосибирск)', max_length=255, null=True, blank=True)
    meta_desc_sam = models.TextField('Meta description (Самара)', max_length=255, null=True, blank=True)
    meta_keyw_spb = models.TextField('Meta keywords (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_keyw_nsk = models.TextField('Meta keywords (Новосибирск)', max_length=255, null=True, blank=True)
    meta_keyw_sam = models.TextField('Meta keywords (Самара)', max_length=255, null=True, blank=True)
    h1_spb = models.CharField('H1 (Санкт-Петербург)', max_length=255, null=True, blank=True)
    h1_nsk = models.CharField('H1 (Новосибирск)', max_length=255, null=True, blank=True)
    h1_sam = models.CharField('H1 (Самара)', max_length=255, null=True, blank=True)
    seo_text_spb = RichTextUploadingField('SEO-текст (Санкт-Петербург)', blank=True)
    seo_text_nsk = RichTextUploadingField('SEO-текст (Новосибирск)', blank=True)
    seo_text_sam = RichTextUploadingField('SEO-текст (Самара)', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key', ]
        verbose_name = 'SEO-настройка'
        verbose_name_plural = 'SEO-настройки'

    def __unicode__(self):
        return self.key

    def get_meta_title(self):
        title = region_field(self, 'title')
        title_suffix = Setting.get_seo_title_suffix()
        # return self.title if self.title else '{} — {}'.format(self.description, title_suffix)
        return title if title else '{} — {}'.format(self.description, title_suffix)

    def get_meta_desc(self):
        # return self.meta_desc if self.meta_desc else self.description
        meta_desc = region_field(self, 'meta_desc')
        return meta_desc if meta_desc else self.description

    def get_meta_keyw(self):
        # return self.meta_keyw if self.meta_keyw else SEOSetting.objects.get(key='global').meta_keyw
        meta_keyw = region_field(self, 'meta_keyw')
        return meta_keyw if meta_keyw else self.description

    def get_h1(self):
        # return self.h1 if self.h1 else self.description
        h1 = region_field(self, 'h1')
        return h1 if h1 else self.description

    def get_seo_text(self):
        seo_text = region_field(self, 'seo_text')
        return seo_text

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

    def show_h1(self):
        return self.h1 if self.h1 else ''
    show_h1.allow_tags = True
    show_h1.short_description = 'H1'

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
    h1 = models.CharField(
        'H1 (на страницах, где он предусмотрен)',
        max_length=255, blank=True,
        help_text='Оставьте пустым, чтобы использовать поле "Заголовок"',
    )
    seo_text = RichTextUploadingField('SEO-текст', blank=True)

    meta_title_spb = models.CharField('Meta title (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_title_nsk = models.CharField('Meta title (Новосибирск)', max_length=255, null=True, blank=True)
    meta_title_sam = models.CharField('Meta title (Самара)', max_length=255, null=True, blank=True)
    meta_desc_spb = models.CharField('Meta description (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_desc_nsk = models.CharField('Meta description (Новосибирск)', max_length=255, null=True, blank=True)
    meta_desc_sam = models.CharField('Meta description (Самара)', max_length=255, null=True, blank=True)
    meta_keyw_spb = models.CharField('Meta keywords (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_keyw_nsk = models.CharField('Meta keywords (Новосибирск)', max_length=255, null=True, blank=True)
    meta_keyw_sam = models.CharField('Meta keywords (Самара)', max_length=255, null=True, blank=True)
    h1_spb = models.CharField('H1 (Санкт-Петербург)', max_length=255, null=True, blank=True)
    h1_nsk = models.CharField('H1 (Новосибирск)', max_length=255, null=True, blank=True)
    h1_sam = models.CharField('H1 (Самара)', max_length=255, null=True, blank=True)
    seo_text_spb = RichTextUploadingField('SEO-текст (Санкт-Петербург)', blank=True)
    seo_text_nsk = RichTextUploadingField('SEO-текст (Новосибирск)', blank=True)
    seo_text_sam = RichTextUploadingField('SEO-текст (Самара)', blank=True)

    class Meta:
        abstract = True

    def get_title(self):
        return self.title

    def get_h1_title(self):
        return self.get_title()

    def get_meta_title(self):
        meta_title = region_field(self, 'meta_title')
        title_suffix = Setting.get_seo_title_suffix()
        # return self.meta_title if self.meta_title else '{} — {}'.format(self.get_title(), title_suffix)
        return meta_title if meta_title else '{} — {}'.format(self.get_title(), title_suffix)

    def get_meta_desc(self):
        return self.meta_desc if self.meta_desc else self.get_title()

    def get_meta_desc(self):
        # return self.meta_desc if self.meta_desc else self.get_title()
        meta_desc = region_field(self, 'meta_desc')
        return meta_desc if meta_desc else self.get_title()

    def get_meta_keyw(self):
        # return self.meta_keyw if self.meta_keyw else SEOSetting.objects.get(key='global').meta_keyw
        meta_keyw = region_field(self, 'meta_keyw')
        return meta_keyw if meta_keyw else SEOSetting.objects.get(key='global').meta_keyw

    def get_h1(self):
        # return self.h1 if self.h1 else self.get_h1_title()
        h1 = region_field(self, 'h1')
        return h1 if h1 else self.get_h1_title()

    def get_seo_text(self):
        # seo_text = self.seo_text
        seo_text = region_field(self, 'seo_text')
        return seo_text

    def has_seo_text(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.seo_text 
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'
