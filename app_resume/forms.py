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


class InstitutionForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование учебного учреждения"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    website_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    diploma = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Institution
        fields = ['title', 'description', 'website_url', 'diploma']


class AdditionalEducationCreateForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))


class AdditionalEducationForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))
    website_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    diploma = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = AdditionalEducation
        fields = ['title', 'description', 'website_url', 'diploma']


class ElectronicCertificateForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': "Наименование пройденного курса"}))
    certificate_url = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    certificate = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    completion_percentage = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range',
                                                                               'class': 'form-range',
                                                                               'min': '0',
                                                                               'max': '100'}))

    class Meta:
        model = ElectronicCertificate
        fields = ['title', 'certificate_url', 'certificate', 'completion_percentage']
