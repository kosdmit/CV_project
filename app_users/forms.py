from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


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


class CreateProfileForm(forms.ModelForm):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    birthday_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control w-50'}), required=False)
    gender = forms.CharField(widget=forms.Select(attrs={'class': 'form-control w-50'}, choices=GENDER_CHOICES), required=False)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control w-50'}), required=False)
    avatar = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control w-50'}), required=False)

    class Meta:
        model = Profile
        fields = ('birthday_date', 'gender', 'phone_number', 'avatar')


