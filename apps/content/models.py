# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import urlparse

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models

# from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from crequest.middleware import CrequestMiddleware
from easy_thumbnails.fields import ThumbnailerImageField
from embed_video.fields import EmbedVideoField
from embed_video.backends import detect_backend
import requests
# from tinymce.models import HTMLField

from ..blog.models import Post
from ..catalog.models import Product
from ..settings.models import SEOSetting, MetatagModel


class Video(MetatagModel):
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('В URL', max_length=127)
    video = EmbedVideoField('Ссылка на видео')
    video_cover = ThumbnailerImageField('Обложка с YouTube', upload_to='videos/yt/covers/',
                                        null=True, blank=True)
    cover = ThumbnailerImageField('Обложка', upload_to='videos/covers/', null=True, blank=True)
    text = RichTextUploadingField('Текст', blank=True, null=True)
    # text = RichTextField('Текст', blank=True, null=True)
    # text = HTMLField('Текст', blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='videos', null=True, blank=True)
    products = models.ManyToManyField(Product, verbose_name='Товары', related_name='video_set', blank=True)
    post = models.ForeignKey(Post, verbose_name='Пост в блоге', related_name='videos', null=True, blank=True)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)
    show_at_list = models.BooleanField('Показывать в списке на странице "видео"', default=True)
    order = models.IntegerField('Порядок', default=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-add_dt', ]
        verbose_name = 'видео'
        verbose_name_plural = 'видео'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        For sitemap.xml lastmod purposes
        (and for updating cover from youtube)
        """
        SEOSetting.objects.get(key='video').save()
        return super(Video, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('video', kwargs={'slug': self.slug, 'pk': self.pk})

    def get_cover_url(self):
        cover_url = (self.cover['video_preview'].url if self.cover
                     else self.get_video_cover())
        request = CrequestMiddleware.get_request()
        if cover_url and request and request.scheme == 'https':
            cover_url = cover_url.replace('http://', 'https://', 1)
        return cover_url

    def get_backend(self):
        backend = detect_backend(self.video)
        return backend

    def get_video_code(self):
        backend = self.get_backend()
        return backend.code

    def get_video_id(self):
        return self.get_video_code()

    def get_video_cover(self):
        backend = self.get_backend()
        return backend.thumbnail

    def get_title(self):
        return '{} — Видео'.format(self.title)

    def get_h1_title(self):
        return self.title

    def get_text(self):
        return self.seo_text or self.text

    def update_video_cover(self, save=True):
        cover_url = self.get_video_cover()
        r = requests.get(cover_url)

        if r.status_code == requests.codes.ok:
            try:
                img_temp = NamedTemporaryFile()
                img_temp.write(r.content)
                img_temp.flush()

                img_filename = urlparse.urlsplit(cover_url).path[1:]
                img_filename = img_filename.split('/')[-1]
                img_filename = '{}/{}'.format(self.get_video_id(), img_filename)
                if not img_filename.count('.'):
                    img_filename = '{}.jpg'.format(img_filename)

                self.video_cover.save(img_filename, File(img_temp), save=True)

            except Exception as e:
                print 'udpate video cover exception: ', e.__class__

    @property
    def thumb_url(self):
        photo = self.video_cover or self.cover
        return photo['product_photo_thumb'].url if photo else self.get_video_cover()

    @property
    def preview_url(self):
        photo = self.video_cover or self.cover
        return photo['product_photo_preview'].url if photo else self.get_video_cover()

    def show_products(self):
        return ', '.join(list(self.products.all().values_list('title', flat=True))) or ''
    show_products.allow_tags = True
    show_products.short_description = 'Товары'


class Page(MetatagModel):
    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('Адрес в url', max_length=255, unique=True)
    image = ThumbnailerImageField('Картинка', null=True, blank=True)
    image_attributes = models.CharField('Атрибуты alt и title у картинки',
                                        max_length=255, blank=True,
                                        help_text='По умолчанию берутся из поля "Заголовок"')
    text = RichTextUploadingField('Текст')
    # text = RichTextField('Текст')
    # text = HTMLField('Текст')
    order = models.IntegerField('Порядок', default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title', ]
        verbose_name = 'страница'
        verbose_name_plural = 'текстовые страницы'

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        s = super(Page, self).save(*args, **kwargs)
        for item in self.menu_items.all():
            item.update_link_from_page()
        return s

    def get_absolute_url(self):
        return reverse('page', kwargs={'slug': self.slug})

    @property
    def image_alt(self):
        return self.image_attributes or self.title


class Menu(models.Model):
    title = models.CharField('Название', max_length=255)
    slug = models.SlugField('Уникальный идентификатор', unique=True)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'меню'
        verbose_name_plural = 'меню'

    def __unicode__(self):
        return self.title


class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, verbose_name='Меню', related_name='items')
    page = models.ForeignKey(Page, verbose_name='Страница', related_name='menu_items', null=True, blank=True)
    label = models.CharField('Название', max_length=255)
    link = models.CharField('Ссылка', max_length=255, null=True, blank=True)
    target_blank = models.BooleanField('Открывать в новой вкладке', default=False)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'пункт меню'
        verbose_name_plural = 'пункты меню'

    def __unicode__(self):
        return self.label

    def update_link_from_page(self, save=True):
        page = self.page
        if page:
            self.link = page.slug
            for lang_code, lang_verbose in settings.LANGUAGES:
                slug = getattr(page, 'slug_{}'.format(lang_code))
                if lang_code == 'ru':
                    setattr(self, 'link_{}'.format(lang_code), '/{}/'.format(slug))
                else:
                    setattr(self, 'link_{}'.format(lang_code), '/{}/{}/'.format(lang_code, slug))
        if save is True:
            self.save(update_link=False)

    def save(self, update_link=True, *args, **kwargs):
        if update_link is True:
            self.update_link_from_page(save=False)
        return super(MenuItem, self).save(*args, **kwargs)


import os
from django.conf import settings
from django.dispatch import receiver
from rosetta.signals import post_save


@receiver(post_save)
def restart_server(sender, **kwargs):
    touchme_path = getattr(settings, 'UWSGI_TOUCHME', '')
    if touchme_path:
        os.system('sleep 1 && touch {}'.format(touchme_path))
