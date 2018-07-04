# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from ..cart.models import Cart
from .admin_forms import UserCreationForm, UserChangeForm
from .models import Profile


admin.site.unregister(Group)


class CartInline(admin.TabularInline):
    model = Cart
    fields = ('checkout_date', 'admin_show_summary', 'count', 'status', 'country', 'city',
              'delivery_method', 'payment_method',)
    readonly_fields = ('checkout_date', 'admin_show_summary', 'count', 'country', 'city',
                       'delivery_method', 'payment_method',)
    suit_classes = 'suit-tab suit-tab-orders'
    extra = 0
    show_change_link = True

    def has_add_permission(self, request):
        return None

    def has_delete_permission(self, request, obj=None):
        return None

    def get_queryset(self, *args, **kwargs):
        qs = super(CartInline, self).get_queryset(*args, **kwargs)
        qs = qs.prefetch_related('cartitem_set', 'certificatecartitem_set').filter(checked_out=True)
        return qs


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'email', 'name', 'country', 'city', 'subscription', 'is_active', 'is_staff', 'is_superuser',)
    list_editable = ('subscription', 'is_active',)
    list_display_links = ('email',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',)
    list_per_page = 200
    suit_form_tabs = (
        ('default', 'Профиль'),
        ('socials', 'Социальные сети'),
        ('orders', 'Заказы'),
    )
    fieldsets = (
        # Настройки юзера
        ('Основные данные', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('email', 'name', 'date_joined', 'subscription',)
        }),
        ('Данные для доставки', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('country', 'city', 'postal_code', 'address', 'phone', 'delivery_method', 'payment_method',)
        }),
        ('Управление доступами', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('is_superuser', 'is_staff', 'is_active', 'groups',),
        }),
        ('Пароль', {
            'classes': ('wide', 'suit-tab', 'suit-tab-default',),
            'fields': ('new_password', 'new_password_repeat'),
        }),
        ('Facebook', {
            'classes': ('suit-tab', 'suit-tab-socials',),
            'fields': ('fb_id', 'fb_name', 'fb_link',)
        }),
        ('VK', {
            'classes': ('suit-tab', 'suit-tab-socials',),
            'fields': ('vk_id', 'vk_name', 'vk_link',)
        }),
        ('Google+', {
            'classes': ('suit-tab', 'suit-tab-socials',),
            'fields': ('gp_id', 'gp_name', 'gp_link',)
        }),
        ('Instagram', {
            'classes': ('suit-tab', 'suit-tab-socials',),
            'fields': ('ig_id', 'ig_name', 'ig_link',)
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'is_staff', 'is_superuser', 'password', 'password_repeat',)
        }),
    )
    inlines = [CartInline, ]
    search_fields = ['email', ]
    readonly_fields = ['date_joined', ]
    ordering = ('-id',)
