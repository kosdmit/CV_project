from django import forms
from django.utils.safestring import mark_safe

from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, ElectronicCertificate


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['about_me', 'soft_skills', 'position']


class ResumeAboutMeForm(forms.Form):
    about_me = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control',
                                                            'rows': '3'}))


class ResumeSoftSkillsForm(forms.Form):
    soft_skills = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'rows': '3'}))


class MainEducationForm(forms.ModelForm):
    EDUCATION_LEVELS = [
        ('Basic General', 'Основное общее образование'),
        ('Secondary General', 'Cреднее (полное) общее образование'),
        ('Vocational education', 'Cреднее профессиональное образование'),
        ('Higher education', 'Высшее образование'),
    ]

    DEGREES = [
        ('Bachelor', 'Бакалавр'),
        ('Specialist', 'Специалист'),
        ('Master', 'Магистр'),
    ]

    level = forms.ChoiceField(choices=EDUCATION_LEVELS,
                              widget=forms.Select(attrs={'class': 'form-select'}))
    degree = forms.ChoiceField(choices=DEGREES,
                               widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = MainEducation
        fields = ['level', 'degree']


class InstitutionCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование"}))


class InstitutionForm(forms.ModelForm):
    title = forms.CharField(
        label='Наименование учебного учреждения:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Наименование"}),
    )

    description = forms.CharField(
        label='Описание',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'descriptionHelp',
                                     'rows': '3'}),
    )

    website_url = forms.URLField(
        label='Веб-сайт:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    diploma = forms.FileField(
        label='Диплом об окончании:',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    completion_date = forms.DateField(
        label='Дата окончания:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    class Meta:
        model = Institution
        fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']


class AdditionalEducationCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))


class AdditionalEducationForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    website_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    diploma = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = AdditionalEducation
        fields = ['title', 'description', 'website_url', 'diploma']


class ElectronicCertificateCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))


class ElectronicCertificateForm(forms.ModelForm):

    certificate_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    certificate = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    completion_percentage = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range',
                                                                               'class': 'form-range',
                                                                               'min': '0',
                                                                               'max': '100'}))

    class Meta:
        model = ElectronicCertificate
        fields = ['title', 'certificate_url', 'certificate', 'completion_percentage']
