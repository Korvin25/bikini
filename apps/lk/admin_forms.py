# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from .models import Profile


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_repeat = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ('email', 'is_active', 'is_staff', 'is_superuser',)

    def clean_password_repeat(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')

        if password and password_repeat and password != password_repeat:
            raise forms.ValidationError('Пароли не совпадают.')

        return password_repeat

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password_repeat = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = '__all__'

    def clean_new_password_repeat(self):
        new_password = self.cleaned_data.get('new_password')
        new_password_repeat = self.cleaned_data.get('new_password_repeat')
        if new_password and new_password_repeat and new_password != new_password_repeat:
            raise forms.ValidationError('Пароли не совпадают.')
        return new_password_repeat

    def save(self, commit=True):
        user = super(UserChangeForm, self).save(commit=False)
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user
