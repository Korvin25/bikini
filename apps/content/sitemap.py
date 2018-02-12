# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from django.utils import timezone

from ..blog import models as blog_models
from ..catalog import models as catalog_models
from ..contests.models import Contest, Participant
from ..settings.models import SEOSetting
from .models import Video, Page


'''
priority - для главной: 1; для разделов: 0.9, для подразделов: 0.8, и т.п.; для объектов - 0.2
changefreq - главная: always;
             разделы: hourly;
             подразделы: daily;
             объекты: weekly;
             снятые с публикации объявления - never
'''


# ------------------
# Главная
# ------------------

class HomeSitemap(Sitemap):
    changefreq = 'always'
    priority = 1

    def items(self):
        return '/'

    def location(self, obj):
        return reverse('home')

    def lastmod(self, obj):
        return timezone.now().date()


# --------------------
# Общее 
# --------------------

class SectionBaseSitemap(Sitemap):
    changefreq = 'hourly'
    priority = '0.9'

    def items(self):
        return []

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class SubSectionBaseSitemap(Sitemap):
    changefreq = 'daily'
    priority = '0.8'

    def items(self):
        return []

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


class ObjectBaseSitemap(Sitemap):
    changefreq = 'weekly'
    priority = '0.2'

    def items(self):
        return []

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.updated_at


# --------------------
# Статические страницы 
# --------------------

class SectionsSitemap(SectionBaseSitemap):

    def items(self):
        self.lastmods = {s.key: s.updated_at for s in SEOSetting.objects.all()}
        return [
            {'reverse': 'certificate', 'seo_slug': 'certificate'},
            {'reverse': 'women', 'seo_slug': 'women'},
            {'reverse': 'men', 'seo_slug': 'men'},
            {'reverse': 'videos', 'seo_slug': 'video'},
            {'reverse': 'blog:home', 'seo_slug': 'blog'},
            {'reverse': 'contests:home', 'seo_slug': 'contests'},
        ]

    def location(self, obj):
        return reverse(obj['reverse'])

    def lastmod(self, obj):
        return self.lastmods.get(obj['seo_slug'], None)


class PagesSitemap(SectionBaseSitemap):

    def items(self):
        return Page.objects.all()


# ----------------------------------------
# Каталог: категории и товары
# ----------------------------------------

class CatalogCategoriesSitemap(SubSectionBaseSitemap):

    def items(self):
        return catalog_models.Category.objects.all()


class CatalogProductsSitemap(ObjectBaseSitemap):

    def items(self):
        products = catalog_models.Product.objects.prefetch_related('categories').filter(show=True)
        items = [{'product': product, 'category': category}
                  for product in products
                  for category in product.categories.all()]
        return items

    def location(self, obj):
        return obj['product'].get_absolute_url(category=obj['category'])

    def lastmod(self, obj):
        return obj['product'].updated_at


# ----------------------------------------
# Блог: категории и посты
# ----------------------------------------

class BlogCategoriesSitemap(SubSectionBaseSitemap):

    def items(self):
        return blog_models.Category.objects.all()


class BlogPostsSitemap(ObjectBaseSitemap):

    def items(self):
        return blog_models.Post.objects.filter(datetime__lte=timezone.now())


# ----------------------------------------
# Конкурсы: конкурсы и участники
# ----------------------------------------

class ContestsSitemap(SubSectionBaseSitemap):

    def items(self):
        return Contest.objects.filter(show=True, published_dt__lte=timezone.now())


class ParticipantsSitemap(ObjectBaseSitemap):

    def items(self):
        return Participant.objects.select_related('contest').filter(contest__show=True,
                                                                    contest__published_dt__lte=timezone.now())


# ----------------------------------------
# Видео
# ----------------------------------------


class VideosSitemap(ObjectBaseSitemap):

    def items(self):
        return Video.objects.all()


# ------------------

sitemaps = {
    'home': HomeSitemap,

    'sections': SectionsSitemap,
    'pages': PagesSitemap,

    'catalog_categories': CatalogCategoriesSitemap,
    'catalog_products': CatalogProductsSitemap,

    # + месяцы?
    'blog_categories': BlogCategoriesSitemap,
    'blog_posts': BlogPostsSitemap,

    'contests': ContestsSitemap,
    'participants': ParticipantsSitemap,

    'videos': VideosSitemap,
}
