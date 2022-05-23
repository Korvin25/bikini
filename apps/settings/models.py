# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ckeditor_uploader.fields import RichTextUploadingField
from easy_thumbnails.fields import ThumbnailerImageField
from solo.models import SingletonModel

from ..core.regions_utils import region_field, get_region_seo_suffix


class Settings(SingletonModel):
    title_mailing = models.CharField('Title для mailing', max_length=255, default='')
    feedback_email = models.TextField('Email для отправки уведомлений с сайта',
                                      default='v.valych@yandex.ru\r\nBikinimini@inbox.ru\r\nalen-rybakova@yandex.ru',
                                      help_text='можно несколько; каждый на новой строке')
    orders_email = models.TextField('Email для отправки писем о новых заказах',
                                    default='v.valych@gmail.com\r\nBikinimini@inbox.ru\r\nalen-rybakova@yandex.ru',
                                    help_text='можно несколько; каждый на новой строке')

    title_suffix = models.CharField('Хвост title у страниц', max_length=255, default='интернет магазин мини и микро бикини от Анастасии Ивановской')
    telegram_login = models.CharField('Логин в телеграме', max_length=255, default='@ivanovskaya_anastasia')
    whatsapp_phone = models.CharField('Номер в Whatsapp', max_length=127, default='+7 902 354-38-45')
    phone = RichTextUploadingField('Номер телефона (в шапке и футере)', default='<p>+7 (916) <strong>445-65-55</strong></p>')

    ig_widget = models.TextField('Instagram', default='', blank=True)
    vk_widget = models.TextField('VK', default='', blank=True)
    fb_widget = models.TextField('Facebook', default='', blank=True)
    tw_widget = models.TextField('Twitter', default='', blank=True)

    robots_txt = models.TextField('Содержимое файла /robots.txt', default='User-agent: *\r\nDisallow: \r\nHost: bikinimini.ru\r\nSitemap: https://bikinimini.ru/sitemap.xml')
    ym_code = models.TextField('Код Яндекс.Метрики', default='<!-- Yandex.Metrika counter --> <script type="text/javascript" > (function (d, w, c) { (w[c] = w[c] || []).push(function() { try { w.yaCounter26447493 = new Ya.Metrika({ id:26447493, clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true }); } catch(e) { } }); var n = d.getElementsByTagName("script")[0], s = d.createElement("script"), f = function () { n.parentNode.insertBefore(s, n); }; s.type = "text/javascript"; s.async = true; s.src = "https://mc.yandex.ru/metrika/watch.js"; if (w.opera == "[object Opera]") { d.addEventListener("DOMContentLoaded", f, false); } else { f(); } })(document, window, "yandex_metrika_callbacks"); </script> <noscript><div><img src="https://mc.yandex.ru/watch/26447493" style="position:absolute; left:-9999px;" alt="" /></div></noscript> <!-- /Yandex.Metrika counter -->')
    ga_code = models.TextField('Код Google Analytics', default="""<!-- Global site tag (gtag.js) - Google Analytics -->\r\n<script async src="https://www.googletagmanager.com/gtag/js?id=UA-55369667-1"></script>\r\n<script>\r\n  window.dataLayer = window.dataLayer || [];\r\n  function gtag(){dataLayer.push(arguments);}\r\n  gtag('js', new Date());\r\n \r\n  gtag('config', 'UA-55369667-1');\r\n</script>""")

    cookies_notify = models.TextField('Cookies: текст плашки внизу сайта', default='Наш сайт использует файлы cookies, чтобы улучшить работу и повысить эффективность сайта. Отключение файлов cookies может привести к неполадкам при работе с сайтом и невозможности положить товар в корзину. Продолжая использование сайта, вы соглашаетесь c использованием нами файлов cookies')
    cookies_alert = models.TextField('Cookies: текст всплывающего окна', default='Включите cookies в Вашем браузере!')
    cookies_cart = models.TextField('Cookies: текст на странице /cart/', null=True, blank=True, default='Если выбранный Вами товар не добавился в корзину, в Вашем браузере отключены cookies.')

    CATALOG_SPECIAL_ORDER_CHOICES = (
        ('banner_first', 'Баннер, текст'),
        ('text_first', 'Текст, баннер'),
    )
    catalog_special_banner = ThumbnailerImageField('Баннер с акциями', null=True, blank=True, upload_to='b/catalog/', help_text='Будет выводиться в размере 851x315 px')
    catalog_special_text = RichTextUploadingField('Текст с акциями', default='', null=True, blank=True)
    catalog_special_order = models.CharField('Порядок отображения', choices=CATALOG_SPECIAL_ORDER_CHOICES, max_length=15, default='banner_first',)
    percent_marketplays = models.IntegerField('Процент на который увеличить цену для маркетплейс', blank=True, null=True, default=20)

    class Meta:
        verbose_name = 'Настройки'

    def __unicode__(self):
        return 'Настройки'

    @classmethod
    def get_feedback_emails(cls):
        obj = cls.get_solo()
        return [e.strip() for e in (obj.feedback_email or '').split('\r\n')]

    @classmethod
    def get_orders_emails(cls):
        obj = cls.get_solo()
        return [e.strip() for e in (obj.orders_email or '').split('\r\n')]

    @classmethod
    def get_seo_title_suffix(cls):
        DEFAULT_PREFIX = 'Bikinimini.ru'
        obj = cls.get_solo()
        return obj.title_suffix or DEFAULT_PREFIX

    @classmethod
    def get_robots_txt(cls):
        obj = cls.get_solo()
        return obj.robots_txt

    def get_cookies_alert(self):
        return self.cookies_alert.replace('\r\n', ' ').replace('  ', ' ')

    @property
    def has_catalog_special(self):
        return self.catalog_special_banner or self.catalog_special_text

    @property
    def catalog_special_banner_url(self):
        banner = self.catalog_special_banner
        return banner['catalog_special_banner'].url if banner else ''

    def get_catalog_special_text(self):
        return self.catalog_special_text.replace('<h2>', '<h2 class="title_block">')


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

        region_seo_suffix = get_region_seo_suffix()
        if region_seo_suffix:
            title_suffix = '{} {}'.format(title_suffix, region_seo_suffix)

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
    title_sch = models.CharField('Meta title (Сочи)', max_length=255, null=True, blank=True)
    title_smf = models.CharField('Meta title (Симферополь)', max_length=255, null=True, blank=True)
    title_svs = models.CharField('Meta title (Севастополь)', max_length=255, null=True, blank=True)
    meta_desc_spb = models.TextField('Meta description (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_desc_nsk = models.TextField('Meta description (Новосибирск)', max_length=255, null=True, blank=True)
    meta_desc_sam = models.TextField('Meta description (Самара)', max_length=255, null=True, blank=True)
    meta_desc_sch = models.TextField('Meta description (Сочи)', max_length=255, null=True, blank=True)
    meta_desc_smf = models.TextField('Meta description (Симферополь)', max_length=255, null=True, blank=True)
    meta_desc_svs = models.TextField('Meta description (Севастополь)', max_length=255, null=True, blank=True)
    meta_keyw_spb = models.TextField('Meta keywords (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_keyw_nsk = models.TextField('Meta keywords (Новосибирск)', max_length=255, null=True, blank=True)
    meta_keyw_sam = models.TextField('Meta keywords (Самара)', max_length=255, null=True, blank=True)
    meta_keyw_sch = models.TextField('Meta keywords (Сочи)', max_length=255, null=True, blank=True)
    meta_keyw_smf = models.TextField('Meta keywords (Симферополь)', max_length=255, null=True, blank=True)
    meta_keyw_svs = models.TextField('Meta keywords (Севастополь)', max_length=255, null=True, blank=True)
    h1_spb = models.CharField('H1 (Санкт-Петербург)', max_length=255, null=True, blank=True)
    h1_nsk = models.CharField('H1 (Новосибирск)', max_length=255, null=True, blank=True)
    h1_sam = models.CharField('H1 (Самара)', max_length=255, null=True, blank=True)
    h1_sch = models.CharField('H1 (Сочи)', max_length=255, null=True, blank=True)
    h1_smf = models.CharField('H1 (Симферополь)', max_length=255, null=True, blank=True)
    h1_svs = models.CharField('H1 (Севастополь)', max_length=255, null=True, blank=True)
    seo_text_spb = RichTextUploadingField('SEO-текст (Санкт-Петербург)', blank=True)
    seo_text_nsk = RichTextUploadingField('SEO-текст (Новосибирск)', blank=True)
    seo_text_sam = RichTextUploadingField('SEO-текст (Самара)', blank=True)
    seo_text_sch = RichTextUploadingField('SEO-текст (Сочи)', blank=True)
    seo_text_smf = RichTextUploadingField('SEO-текст (Симферополь)', blank=True)
    seo_text_svs = RichTextUploadingField('SEO-текст (Севастополь)', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key', ]
        verbose_name = 'SEO-настройка'
        verbose_name_plural = 'SEO-настройки'

    def __unicode__(self):
        return self.key

    @classmethod
    def get_default_meta_desc(cls):
        meta_desc = SEOSetting.objects.get(key='global').meta_desc
        region_seo_suffix = get_region_seo_suffix
        if region_seo_suffix:
            meta_desc = '{} {}'.format(meta_desc, region_seo_suffix)
        return meta_desc

    @classmethod
    def get_default_meta_keyw(cls):
        return SEOSetting.objects.get(key='global').meta_keyw

    def get_meta_title(self):
        title = region_field(self, 'title', add_suffix=True)
        if title:
            return title
        title_suffix = Settings.get_seo_title_suffix()
        return '{} — {}'.format(self.description, title_suffix)

    def get_meta_desc(self):
        meta_desc = region_field(self, 'meta_desc')
        return meta_desc if meta_desc else self.description

    def get_meta_keyw(self):
        meta_keyw = region_field(self, 'meta_keyw')
        return meta_keyw if meta_keyw else SEOSetting.get_default_meta_keyw()

    def get_h1(self):
        # return self.h1 if self.h1 else self.description
        h1 = region_field(self, 'h1')
        return h1 if h1 else self.description

    def get_seo_text(self):
        seo_text = region_field(self, 'seo_text', use_default=False)
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
    meta_title_sch = models.CharField('Meta title (Сочи)', max_length=255, null=True, blank=True)
    meta_title_smf = models.CharField('Meta title (Симферополь)', max_length=255, null=True, blank=True)
    meta_title_svs = models.CharField('Meta title (Севастополь)', max_length=255, null=True, blank=True)
    meta_desc_spb = models.CharField('Meta description (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_desc_nsk = models.CharField('Meta description (Новосибирск)', max_length=255, null=True, blank=True)
    meta_desc_sam = models.CharField('Meta description (Самара)', max_length=255, null=True, blank=True)
    meta_desc_sch = models.CharField('Meta description (Сочи)', max_length=255, null=True, blank=True)
    meta_desc_smf = models.CharField('Meta description (Симферополь)', max_length=255, null=True, blank=True)
    meta_desc_svs = models.CharField('Meta description (Севастополь)', max_length=255, null=True, blank=True)
    meta_keyw_spb = models.CharField('Meta keywords (Санкт-Петербург)', max_length=255, null=True, blank=True)
    meta_keyw_nsk = models.CharField('Meta keywords (Новосибирск)', max_length=255, null=True, blank=True)
    meta_keyw_sam = models.CharField('Meta keywords (Самара)', max_length=255, null=True, blank=True)
    meta_keyw_sch = models.CharField('Meta keywords (Сочи)', max_length=255, null=True, blank=True)
    meta_keyw_smf = models.CharField('Meta keywords (Симферополь)', max_length=255, null=True, blank=True)
    meta_keyw_svs = models.CharField('Meta keywords (Севастополь)', max_length=255, null=True, blank=True)
    h1_spb = models.CharField('H1 (Санкт-Петербург)', max_length=255, null=True, blank=True)
    h1_nsk = models.CharField('H1 (Новосибирск)', max_length=255, null=True, blank=True)
    h1_sam = models.CharField('H1 (Самара)', max_length=255, null=True, blank=True)
    h1_sch = models.CharField('H1 (Сочи)', max_length=255, null=True, blank=True)
    h1_smf = models.CharField('H1 (Симферополь)', max_length=255, null=True, blank=True)
    h1_svs = models.CharField('H1 (Севастополь)', max_length=255, null=True, blank=True)
    seo_text_spb = RichTextUploadingField('SEO-текст (Санкт-Петербург)', blank=True)
    seo_text_nsk = RichTextUploadingField('SEO-текст (Новосибирск)', blank=True)
    seo_text_sam = RichTextUploadingField('SEO-текст (Самара)', blank=True)
    seo_text_sch = RichTextUploadingField('SEO-текст (Сочи)', blank=True)
    seo_text_smf = RichTextUploadingField('SEO-текст (Симферополь)', blank=True)
    seo_text_svs = RichTextUploadingField('SEO-текст (Севастополь)', blank=True)

    class Meta:
        abstract = True

    def get_title(self):
        return self.title

    def get_h1_title(self):
        return self.get_title()

    def get_meta_title(self):
        meta_title = region_field(self, 'meta_title', add_suffix=True)
        if meta_title:
            return meta_title
        title_suffix = Settings.get_seo_title_suffix()
        return '{} — {}'.format(self.get_title(), title_suffix)

    def get_meta_desc(self):
        meta_desc = region_field(self, 'meta_desc')
        return meta_desc if meta_desc else self.get_title()

    def get_meta_keyw(self):
        meta_keyw = region_field(self, 'meta_keyw')
        return meta_keyw if meta_keyw else SEOSetting.get_default_meta_keyw()

    def get_h1(self):
        h1 = region_field(self, 'h1')
        return h1 if h1 else self.get_h1_title()

    def get_seo_text(self):
        # seo_text = self.seo_text
        seo_text = region_field(self, 'seo_text', use_default=False)
        return seo_text

    def has_seo_text(self):
        return ('<img src="/static/admin/img/icon-yes.svg" alt="True">' if self.seo_text 
                else '<img src="/static/admin/img/icon-no.svg" alt="False">')
    has_seo_text.allow_tags = True
    has_seo_text.short_description = 'Есть SEO-текст?'
