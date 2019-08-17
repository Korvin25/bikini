# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.views.generic import TemplateView, RedirectView

# from solid_i18n.urls import solid_i18n_patterns

from apps.analytics.views import SetYMClientIDView
from apps.cart.views import CartView, CartGetDiscountView
from apps.cart.certificate.views import CertificateView
from apps.catalog.views import ProductsView, ProductView, ProductWithDiscountView
from apps.catalog.api_views import IncreaseInStockView, ChangeProductView
from apps.content.sitemap import sitemaps
from apps.content.views import HomepageView, VideoListView, VideoDetailView, PageView, robots_txt
from apps.currency.views import SetCurrencyView
from apps.lk.views import (ProfileHomeView, ProfileResetPasswordView, ProfileSetPasswordView,
                           ProfileFormView, ProfileSetPasswordFormView,)
from apps.views import PhotoUploadView


urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^ajax/upload/$', PhotoUploadView.as_view(), name='photo_upload'),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),

    url(r'^robots\.txt$', robots_txt, name='robots_txt'),
    # url(r'^robots\.txt/$', RedirectView.as_view(pattern_name='robots_txt', permanent=True)),
    url(r'^robots\.txt/$', RedirectView.as_view(pattern_name='robots_txt', permanent=False)),

    url(r'^yandex_32b44e0eb9e4fa78\.html$', TemplateView.as_view(template_name='ya_verification.html')),

    url(r'^404/$', TemplateView.as_view(template_name='404.html')),


    # # api
    # url(r'^api/cart/', include('apps.cart.api.urls', namespace='cart_api')),
    # url(r'^api/certificate/', include('apps.cart.certificate.urls', namespace='certificate_api')),
    # url(r'^api/auth/', include('apps.lk.auth.urls', namespace='auth')),
    # url(r'^api/profile/edit/', ProfileFormView.as_view(), name='profile-edit'),
    # url(r'^api/forms/', include('apps.feedback.urls', namespace='forms')),
    # url(r'^api/currency/set/', SetCurrencyView.as_view(), name='set_currency'),

    # 3rd party apps
    # url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^admin/salmonella/', include('salmonella.urls')),
    url(r'^filer/', include('filer.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    # seo
    url(r'^sitemap\.xml$', sitemap_view, {'sitemaps': sitemaps}),
]


urlpatterns += i18n_patterns(
    # -- home --
    url(r'^$', HomepageView.as_view(), name='home'),

    # -- api --
    url(r'^api/cart/', include('apps.cart.api.urls', namespace='cart_api')),
    url(r'^api/certificate/', include('apps.cart.certificate.urls', namespace='certificate_api')),
    url(r'^api/auth/', include('apps.lk.auth.urls', namespace='auth')),
    url(r'^api/profile/edit/', ProfileFormView.as_view(), name='profile-edit'),
    url(r'^api/profile/set_password/', ProfileSetPasswordFormView.as_view(), name='profile-set-password-form'),
    url(r'^api/forms/', include('apps.feedback.urls', namespace='forms')),
    url(r'^api/currency/set/', SetCurrencyView.as_view(), name='set_currency'),
    url(r'^api/analytics/client_id/', SetYMClientIDView.as_view(), name='set_ym_client_id'),
    # (admin api)
    url(r'^api/products/increase_in_stock/', IncreaseInStockView.as_view(), name='admin_increase_in_stock'),
    url(r'^api/products/change/', ChangeProductView.as_view(), name='admin_change_product'),

    # -- apps --
    url(r'^cart/$', CartView.as_view(), name='cart'),
    url(r'^cart/get_discount/(?P<pk>\d+)/$', CartGetDiscountView.as_view(), name='cart_get_discount'),
    url(r'^certificate/$', CertificateView.as_view(), name='certificate'),
    url(r'^profile/$', ProfileHomeView.as_view(), name='profile'),
    url(r'^profile/reset_password/(?P<signature>[^/]+)/$', ProfileResetPasswordView.as_view(), name='profile_reset_password'),
    url(r'^profile/set_password/$', ProfileSetPasswordView.as_view(), name='profile_set_password'),

    url(r'^women/$', ProductsView.as_view(with_category=False, sale_category=False, sex='female'), name='women'),
    url(r'^muzhskie-bikini/$', ProductsView.as_view(with_category=False, sale_category=False, sex='male'), name='men'),
    url(r'^women/specialnoe-predlogenie/$', ProductsView.as_view(with_category=False, sale_category=True, sex='female'), name='women_sale'),
    url(r'^muzhskie-bikini/specialnoe-predlogenie/$', ProductsView.as_view(with_category=False, sale_category=True, sex='male'), name='men_sale'),
    url(r'^women/(?P<slug>[^/]+)/$', ProductsView.as_view(with_category=True, sale_category=False, sex='female'), name='women_category'),
    url(r'^muzhskie-bikini/(?P<slug>[^/]+)/$', ProductsView.as_view(with_category=True, sale_category=False, sex='male'), name='men_category'),
    url(r'^women/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/$', ProductView.as_view(sex='female'), name='women_product'),
    url(r'^muzhskie-bikini/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/$', ProductView.as_view(sex='male'), name='men_product'),
    url(r'^women/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/discount/(?P<category_id>\d+)/(?P<code>[^/]+)/$',
        ProductWithDiscountView.as_view(sex='female'), name='women_product_with_discount'),
    url(r'^muzhskie-bikini/(?P<category_slug>[^/]+)/(?P<slug>[^/]+)-(?P<pk>\d+)/discount/(?P<category_id>\d+)/(?P<code>[^/]+)/$',
        ProductWithDiscountView.as_view(sex='male'), name='men_product_with_discount'),

    url(r'^video/$', VideoListView.as_view(), name='videos'),
    url(r'^video/(?P<slug>[^/]+)-(?P<pk>\d+)/$', VideoDetailView.as_view(), name='video'),

    url(r'^blog/', include('apps.blog.urls', namespace='blog')),
    url(r'^contests/', include('apps.contests.urls', namespace='contests')),
    url(r'^wishlist/', include('apps.lk.wishlist.urls', namespace='wishlist')),

    url(r'^(?P<slug>[^/]+)/$', PageView.as_view(), name='page'),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
