# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from apps.lk.models import Profile


class LoginForm(forms.Form):
    """
    Форма логина
    """
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        if not self._errors:
            email = cleaned_data.get('email')
            password = cleaned_data.get('password')
            try:
                user = Profile.objects.get(email__iexact=email)
                if not user.check_password(password):
                    raise forms.ValidationError('Неверное сочетание Email / Пароль.')
                elif not user.is_active:
                    raise forms.ValidationError('Пользователь с данным email заблокирован.')
            except Profile.DoesNotExist:
                raise forms.ValidationError('Неверное сочетание Email / Пароль.')
        return cleaned_data


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField(label="E-mail")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    name = forms.CharField(label="ФИО")

    class Meta:
        model = Profile
        fields = ('email', 'name',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email__iexact=email).count():
            raise forms.ValidationError('Профиль с таким email уже существует.')
        return email

    def save(self, commit=True):
        profile = super(RegistrationForm, self).save(commit=False)
        profile.set_password(self.cleaned_data['password'])
        if commit:
            profile.save()
        return profile


class ResetPasswordForm(forms.Form):
    """
    Форма восстановления пароля
    """
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        if not self._errors:
            email = cleaned_data.get('email')
            try:
                Profile.objects.get(email__iexact=email)
            except Profile.DoesNotExist:
                raise forms.ValidationError('Пользователя с таким email не существует.')
        return cleaned_data
