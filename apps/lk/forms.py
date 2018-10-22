# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Profile


class ProfileForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ('subscription', 'name', 'country', 'city', 'postal_code', 'address', 'phone', 'email',)

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != self.instance.email:
            if Profile.objects.filter(email__iexact=email).count():
                raise forms.ValidationError(_('Такой email уже занят.'))
        return email

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if old_password:
            if not self.instance.check_password(old_password):
                raise forms.ValidationError(_('Неверный пароль.'))
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password', '').strip()
        if new_password:
            old_password = self.cleaned_data.get('old_password')
            if not old_password and self.instance.has_password:
                if self.data.get('old_password'):
                    # значит, старый пароль был неправильный и не попал в self.data
                    return None
                else:
                    raise forms.ValidationError(_('Введите старый пароль.'))
        return new_password

    def save(self, commit=True):
        user = super(ProfileForm, self).save(commit=False)
        if self.cleaned_data.get('email'):
            user.has_email = True
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
            user.has_password = True
        if commit:
            user.save()
        return user


class ResetPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        if not self._errors:
            email = cleaned_data.get('email')
            try:
                Profile.objects.get(email__iexact=email)
            except Profile.DoesNotExist:
                raise forms.ValidationError(_('Пользователя с таким email не существует.'))
        return cleaned_data


class SetPasswordForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_repeat = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ('name',)

    def clean(self):
        cleaned_data = super(SetPasswordForm, self).clean()

        if not self._errors:
            new_password = cleaned_data.get('new_password')
            new_password_repeat = cleaned_data.get('new_password_repeat')

            if not new_password == new_password_repeat:
                raise forms.ValidationError(_('Пароли не совпадают'))
            else:
                return cleaned_data

    def save(self, commit=True):
        profile = self.instance

        profile.set_password(self.cleaned_data['new_password'])
        profile.has_password = True
        profile.signature = ''

        if commit:
            profile.save()
        return profile
