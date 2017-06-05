# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .admin_forms import UserCreationForm, UserChangeForm
from .models import Profile


admin.site.unregister(Group)


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('id', 'email', 'is_active', 'is_staff', 'is_superuser',)
    list_display_links = ('email',)
    list_filter = ('is_active', 'is_staff', 'is_superuser',)
    list_per_page = 200

    fieldsets = (
        # Настройки юзера
        ('Данные', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('email', 'date_joined',)
        }),
        ('Управление доступами', {
            'classes': ('suit-tab', 'suit-tab-default',),
            'fields': ('is_superuser', 'is_staff', 'is_active',),
        }),
        ('Пароль', {
            'classes': ('wide', 'suit-tab', 'suit-tab-default',),
            'fields': ('new_password', 'new_password_repeat'),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('email', 'is_staff', 'is_superuser', 'password', 'password_repeat',)
        }),
    )
    search_fields = ['email', ]
    readonly_fields = ['date_joined', ]
    ordering = ('-id',)
