from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

import app_resume.models
from .models import Profile, SocialLinks

from django.utils.translation import gettext_lazy as _


class SignUpUserForm(UserCreationForm):
    username = forms.CharField(
        label='Логин для входа:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'aria-describedby': "usernameHelp",
                                      }))

    email = forms.EmailField(
        label='Email:',
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                       'aria-describedby': "emailHelp",
                                       }))

    password1 = forms.CharField(
        label='Пароль:',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'id': 'password1_field'}))

    password2 = forms.CharField(
        label='Повторите пароль:',
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'id': 'password2_field'}))

    first_name = forms.CharField(
        label='Имя:',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'area-describedby': 'first_nameHelp',
                                      }))

    last_name = forms.CharField(
        label='Фамилия:',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'area-describedby': 'last_nameHelp',
                                      }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')


class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label='Имя пользователя:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'area-describedby': 'usernameHelp',
                                      }))

    first_name = forms.CharField(
        label='Имя:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'area-describedby': 'first_nameHelp',
                                      }))

    last_name = forms.CharField(
        label='Фамилия:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'area-describedby': 'last_nameHelp',
                                      }))

    email = forms.EmailField(
        label='Адрес электронной почты:',
        widget=forms.EmailInput(attrs={'class': 'form-control',
                                       'area-describedby': 'last_nameHelp',
                                       }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CreateProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Муж'),
        ('F', 'Жен'),
        ('O', 'Другое'),
    )

    birthday_date = forms.DateField(
        label='День вашего рождения:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
        required=False
    )

    gender = forms.CharField(
        label='Пол:',
        widget=forms.Select(attrs={'class': 'form-control'},
                            choices=GENDER_CHOICES),
        required=False
    )

    phone_number = forms.CharField(
        label='Телефон:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'value': '+7',
                                      'placeholder': '+7'}),
        required=False
    )

    image = forms.FileField(
        label='Фото профиля:',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ('birthday_date', 'gender', 'phone_number', 'image')


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Имя пользователя:',
        widget=forms.TextInput(attrs={"autofocus": True,
                                      'class': 'form-control',
                                      }))
    password = forms.CharField(
        label='Пароль:',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          'class': 'form-control',
                                          }),
    )


class CreateResumeForm(forms.ModelForm):
    position = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'placeholder': 'Желаемая должность',
                                                             'aria-describedby': "button-addon2",
                                                             }))

    class Meta:
        model = app_resume.models.Resume
        fields = ('position',)


class PrimaryResumeSelectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        instance = kwargs.pop('instance', None)
        super(PrimaryResumeSelectForm, self).__init__(*args, **kwargs)
        self.fields['is_primary'].queryset = \
            app_resume.models.Resume.objects.filter(user=self.user)

        if instance:
            self.fields['is_primary'].initial = instance

    is_primary = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input ms-auto',
                                        'value': '',
                                        'onclick': 'javascript: submit()'}),
    )

    class Meta:
        model = app_resume.models.Resume
        fields = ['is_primary']


class SocialLinksForm(forms.ModelForm):
    twitter = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    facebook = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    linked_in = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    vk = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    instagram = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    hh = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    git_hub = forms.URLField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = SocialLinks
        fields = ['twitter', 'facebook', 'linked_in', 'vk', 'instagram', 'hh', 'git_hub']

