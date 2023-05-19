from django import forms

from app_job_hunt.models import Employer


class RawContactEmployerForm(forms.ModelForm):
    raw_contact = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Email или номер телефона"})
    )

    class Meta:
        model = Employer
        fields = ['raw_contact']