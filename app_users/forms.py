from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import User

import app_resume.models
from .models import Profile

from django.utils.translation import gettext_lazy as _


class SignUpUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50',
                                                             'aria-describedby': "usernameHelp",
                                                             }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control w-50',
                                                            'aria-describedby': "emailHelp",
                                                            }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control w-50'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control w-50'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50',
                                                               'area-describedby': 'first_nameHelp',
                                                               }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50',
                                                               'area-describedby': 'last_nameHelp',
                                                               }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50',
                                                               'area-describedby': 'first_nameHelp',
                                                               }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50',
                                                               'area-describedby': 'last_nameHelp',
                                                               }))

    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CreateProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    birthday_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control w-50',
                                      'type': 'date'}),
        required=False
    )

    gender = forms.CharField(
        widget=forms.Select(attrs={'class': 'form-control w-50'}, choices=GENDER_CHOICES),
        required=False
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control w-50'}),
        required=False
    )

    avatar = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control w-50'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ('birthday_date', 'gender', 'phone_number', 'avatar')


class CustomAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True,
                                                           'class': 'form-control w-50',
                                                           }))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password",
                                          'class': 'form-control w-50',
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
        widget=forms.RadioSelect(attrs={'class': 'form-check-input',
                                        'value': '',
                                        'onclick': 'javascript: submit()'}),
    )

    class Meta:
        model = app_resume.models.Resume
        fields = ['is_primary']
