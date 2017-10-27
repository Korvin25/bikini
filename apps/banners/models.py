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


class PromoBanner(models.Model):
    SLIDER_TYPES = (
        ('unit', 'единичный'),
        ('composite', 'составной (поля добавятся позже)'),
    )
    title = models.CharField('Заголовок баннера', max_length=255, help_text='для показа в админке')
    banner_type = models.CharField('Тип баннера', max_length=15, choices=SLIDER_TYPES, default='unit')

    description_h1 = models.CharField('Описание (h1)', max_length=255, blank=True)
    description_picture = ThumbnailerImageField('Описание (картинка)', upload_to='promo_banner/pictures/',
                                                null=True, blank=True)
    description_picture_alt = models.CharField('Описание (alt у картинки)', max_length=127, blank=True)
    description_p = models.TextField('Описание (текст)', blank=True)
    link = models.URLField('Ссылка')
    link_text = models.CharField('Текст на ссылке', max_length=127, help_text='например, "Перейти в каталог"')

    cover = ThumbnailerImageField('Обложка', upload_to='promo_banner/covers/')
    video = models.URLField('Видео', help_text='Ссылка на youtube.com', null=True, blank=True)
    video_id = models.CharField(null=True, blank=True, max_length=31, editable=False)

    is_enabled = models.BooleanField('Включен?', default=True)
    add_dt = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ['-id', ]
        verbose_name = 'промо-баннер'
        verbose_name_plural = 'промо-баннер на главной'

    def __unicode__(self):
        return self.title

    def get_cover_url(self):
        return (self.cover['homepage_cover'].url if self.cover
                else '/static/images/bg_header.jpg')
                # else 'http://img.youtube.com/vi/{}/mqdefault.jpg'.format(self.video_id))

    def get_iframe_video_link(self):
        return get_youtube_embed_video(video_id=self.video_id)

    @property
    def girl(self):
        girl = self.girls.filter(is_enabled=True).order_by('?').first()
        return girl


class PromoBannerGirl(models.Model):
    banner = models.ForeignKey(PromoBanner, verbose_name='Баннер', related_name='girls')
    name = models.CharField('Имя', max_length=255, blank=True, help_text='необязательное поле; для показа в админке')
    photo = ThumbnailerImageField('Фото', upload_to='promo_banner/girls/', help_text='файл .png')
    is_enabled = models.BooleanField('Включено?', default=True)

    class Meta:
        ordering = ['id', ]
        verbose_name = 'фото модели'
        verbose_name_plural = 'фото моделей'

    def __unicode__(self):
        return self.name or self.photo.name

    def get_photo(self):
        return self.photo['homepage_girl']

    @property
    def margin_left(self):
        return (-118 - ((self.get_photo().width-314) / 2))
