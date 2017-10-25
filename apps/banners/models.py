# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

from easy_thumbnails.fields import ThumbnailerImageField


class ActiveBannerManager(models.Manager):

    def get_queryset(self):
        return super(ActiveBannerManager, self).get_queryset().filter(
            start_datetime__lte=timezone.now(), end_datetime__gte=timezone.now(), show=True
        )


def get_upload_to(self, filename):
    upload_to = 'b/{}/{}'.format(self.location, filename)
    return upload_to


class Banner(models.Model):
    LOCATION_CHOICES = (
        ('left', 'Слева (вертикальный)'),
        ('bottom', 'Снизу (горизонтальный)'),
    )
    title = models.CharField('Заголовок', max_length=255,
                             help_text='Для показа в админке и в атрибутах alt и title')
    image = ThumbnailerImageField('Изображение', upload_to=get_upload_to)
    url = models.URLField('Ссылка', max_length=255, null=True, blank=True)
    button_text = models.CharField('Текст на кнопке', max_length=127, blank=True,
                                   help_text='оставьте пустым, чтобы не выводить кнопку')
    location = models.CharField('Расположение', max_length=10, choices=LOCATION_CHOICES, default='left')

    show = models.BooleanField('Показывать на сайте', default=True)
    target_blank = models.BooleanField('Открывать в новом окне', default=True)
    start_datetime = models.DateTimeField('Начало размещения', default=timezone.now)
    end_datetime = models.DateTimeField('Конец размещения')

    shows = models.IntegerField('Показы', default=0)
    clicks = models.IntegerField('Клики', default=0)

    objects = models.Manager()
    active_objects = ActiveBannerManager()

    class Meta:
        ordering = ['-show', 'location', '-end_datetime', '-start_datetime', ]
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'

    def __unicode__(self):
        location = 'справа' if self.location == 'right' else 'снизу'
        return '{} ({})'.format(self.title, location)

    @property
    def image_url(self):
        return (self.image['footer_banner'].url if self.location == 'bottom'
                else self.image['left_banner'].url if self.location == 'left'
                else self.image.url)

    @property
    def has_text(self):
        return self.lines.count()

    def show_has_text(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.has_text
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    show_has_text.allow_tags = True
    show_has_text.short_description = 'Есть текст?'

    @property
    def has_button(self):
        return self.button_text

    def show_has_button(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.has_button
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    show_has_button.allow_tags = True
    show_has_button.short_description = 'Есть кнопка?'


class BannerTextLine(models.Model):
    banner = models.ForeignKey(Banner, verbose_name='Баннер', related_name='lines')
    line = models.CharField('Строка', max_length=255)
    big = models.BooleanField('Крупный шрифт?', default=False)
    order = models.IntegerField('Порядок', default=10)

    class Meta:
        ordering = ['order', 'id', ]
        verbose_name = 'строка'
        verbose_name_plural = 'строки текста'

    def __unicode__(self):
        return self.line
