from django import forms

from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation,\
    ElectronicCertificate, WorkExpSection, Job


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['about_me', 'soft_skills', 'position']


class ResumePositionForm(forms.ModelForm):
    position = forms.CharField(
        label='Желаемая должность:',
        widget=forms.TextInput(attrs={'class': 'form-control',})
    )

    class Meta:
        model = Resume
        fields = ('position',)


class ResumeAboutMeForm(forms.ModelForm):
    about_me = forms.CharField(
        label='Расскажите о себе:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': '3'})
    )

    class Meta:
        model = Resume
        fields = ('about_me',)


class ResumeSoftSkillsForm(forms.ModelForm):
    soft_skills = forms.CharField(
        label='Расcкажите о ваших сильных сторонах:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'rows': '3'})
    )

    class Meta:
        model = Resume
        fields = ('soft_skills',)


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

    level = forms.ChoiceField(
        required=False,
        label='Уровень образования:',
        choices=EDUCATION_LEVELS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    degree = forms.ChoiceField(
        required=False,
        label='Степень или квалификация:',
        choices=DEGREES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = MainEducation
        fields = ['level', 'degree']


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

    is_primary = forms.BooleanField(
        required=False,
        label='Сделать главным',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input',
                                          'type': 'checkbox'}),
    )

    class Meta:
        model = Institution
        fields = ['title', 'description', 'website_url', 'diploma', 'completion_date', 'is_primary']


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


class ElectronicCertificateForm(forms.ModelForm):
    title = forms.CharField(
        label='Наименование курса:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Наименование курса курса"})
    )

    certificate_url = forms.URLField(
        required=False,
        label='Cсылка на сертификат:',
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
                                        'class': 'form-range completion-percentage-input',
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


class SkillCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Добавить навык"}))


class WorkExpSectionForm(forms.ModelForm):
    title = forms.CharField(
        label='Заголовок:',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': "Добавить отрасль или период работы"})
    )

    start_date = forms.DateField(
        required=False,
        label='Дата окончания:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    finish_date = forms.DateField(
        required=False,
        label='Дата окончания:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    class Meta:
        model = WorkExpSection
        fields = ['title', 'start_date', 'finish_date']


class JobForm(forms.ModelForm):
    title = forms.CharField(
        label='Проект/Должность',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        required=False,
        label='Описание:',
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'aria-describedby': 'descriptionHelp',
                                     'rows': '3'}),
    )

    project_url = forms.URLField(
        required=False,
        label='Веб-ссылка на проект:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    git_url = forms.URLField(
        required=False,
        label='Ссылка на GitHub:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    start_date = forms.DateField(
        required=False,
        label='Дата начала работы:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    finish_date = forms.DateField(
        required=False,
        label='Дата завершения работы:',
        widget=forms.DateInput(attrs={'class': 'form-control',
                                      'type': 'date'}),
    )

    position = forms.CharField(
        required=False,
        label='Ваша должность:',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    company = forms.CharField(
        required=False,
        label='Компания:',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    company_url = forms.URLField(
        required=False,
        label='Ссылка на сайт компании:',
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Job
        fields = ['title', 'description', 'project_url', 'git_url', 'start_date', 'finish_date', 'position', 'company', 'company_url']


