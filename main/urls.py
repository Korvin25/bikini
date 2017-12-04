# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

# from solid_i18n.urls import solid_i18n_patterns

from apps.catalog.views import ProductsView, ProductView
from apps.content.views import HomepageView, VideoListView, VideoDetailView, PageView


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # pages without language prefixes
    # url(r'^forms/', include('apps.feedback.urls', namespace='forms')),

    # 3rd party apps
    # url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^admin/rosetta/', include('rosetta.urls')),
    url(r'^admin/salmonella/', include('salmonella.urls')),
    url(r'^filer/', include('filer.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
]


urlpatterns += i18n_patterns(
    # pages
    url(r'^$', HomepageView.as_view(), name='home'),
    url(r'^pages/$', TemplateView.as_view(template_name='pages.html'), name='pages'),

    url(r'^konkurs-itog/$', TemplateView.as_view(template_name='konkurs-itog.html'), name='konkurs-itog'),
    url(r'^konkurs-model/$', TemplateView.as_view(template_name='konkurs-model.html'), name='konkurs-model'),
    url(r'^konkurs1/$', TemplateView.as_view(template_name='konkurs1.html'), name='konkurs1'),
    url(r'^my-cut-1/$', TemplateView.as_view(template_name='my-cut-1.html'), name='my-cut-1'),
    url(r'^my-cut-2/$', TemplateView.as_view(template_name='my-cut-2.html'), name='my-cut-2'),
    url(r'^my-cut-3/$', TemplateView.as_view(template_name='my-cut-3.html'), name='my-cut-3'),
    url(r'^my-cut-4/$', TemplateView.as_view(template_name='my-cut-4.html'), name='my-cut-4'),
    url(r'^my-cut-after/$', TemplateView.as_view(template_name='my-cut-after.html'), name='my-cut-after'),
    url(r'^my-cut-spisok/$', TemplateView.as_view(template_name='my-cut-spisok.html'), name='my-cut-spisok'),
    url(r'^my-cut/$', TemplateView.as_view(template_name='my-cut.html'), name='my-cut'),
    url(r'^pd-and-history/$', TemplateView.as_view(template_name='pd-and-history.html'), name='pd-and-history'),
    url(r'^podarochnyi-sertificat/$', TemplateView.as_view(template_name='podarochnyi-sertificat.html'), name='podarochnyi-sertificat'),
    url(r'^spisok-pokupok/$', TemplateView.as_view(template_name='spisok-pokupok.html'), name='spisok-pokupok'),

    url(r'^men-detail/$', TemplateView.as_view(template_name='catalog/men-detail.html'), name='men-detail'),
    url(r'^women-detail/$', TemplateView.as_view(template_name='catalog/women-detail.html'), name='women-detail'),

    url(r'^women/$', ProductsView.as_view(with_category=False, sex='female'), name='women'),
    url(r'^men/$', ProductsView.as_view(with_category=False, sex='male'), name='men'),
    url(r'^women/(?P<slug>[^/]+)/$', ProductsView.as_view(with_category=True, sex='female'), name='women_category'),
    url(r'^men/(?P<slug>[^/]+)/$', ProductsView.as_view(with_category=True, sex='male'), name='men_category'),
    url(r'^women/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/$', ProductView.as_view(sex='female'), name='women_product'),
    url(r'^men/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/$', ProductView.as_view(sex='male'), name='men_product'),

    url(r'^video/$', VideoListView.as_view(), name='videos'),
    url(r'^video/(?P<slug>[^/]+)-(?P<pk>\d+)/$', VideoDetailView.as_view(), name='video'),

    url(r'^blog/$', TemplateView.as_view(template_name='blog.html'), name='blog'),
    url(r'^blog-page/$', TemplateView.as_view(template_name='blog-page.html'), name='blog-page'),

    url(r'^(?P<slug>[^/]+)/$', PageView.as_view(), name='page'),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
