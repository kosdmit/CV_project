from django import forms

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
        ('Other', 'Другое'),
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
        required=False,
        label='Описание',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'descriptionHelp',
                                     'rows': '3'}),
    )

    website_url = forms.URLField(
        required=False,
        label='Веб-сайт:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    diploma = forms.FileField(
        required=False,
        label='Диплом об окончании:',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    completion_date = forms.DateField(
        required=False,
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
    title = forms.CharField(
        label='Наименование учебной программы:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Наименование учебной программы"}),
    )

    description = forms.CharField(
        required=False,
        label='Описание:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'descriptionHelp',
                                     'rows': '3'}),
    )

    website_url = forms.URLField(
        required=False,
        label='Веб-сайт:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    diploma = forms.FileField(
        required=False,
        label='Документ об окончании:',
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    completion_date = forms.DateField(
        required=False,
        label='Дата окончания:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    class Meta:
        model = AdditionalEducation
        fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']


class ElectronicCertificateCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))


class ElectronicCertificateForm(forms.ModelForm):
    title = forms.CharField(
        label='Наименование курса:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Наименование курса курса"})
    )

    certificate_url = forms.URLField(
        required=False,
        label='URL ссылка на электронный сертификат:',
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )

    certificate = forms.FileField(
        required=False,
        label='Сертификат:',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    completion_percentage = forms.IntegerField(
        required=False,
        label='Процент выполнения:',
        widget=forms.NumberInput(attrs={'type': 'range',
                                        'class': 'form-range',
                                        'min': '0',
                                        'max': '100'})
    )

    completion_date = forms.DateField(
        required=False,
        label='Дата окончания:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )


    class Meta:
        model = ElectronicCertificate
        fields = ['title', 'certificate_url', 'certificate', 'completion_percentage', 'completion_date']
