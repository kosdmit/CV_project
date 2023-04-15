from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, AdditionalEducationForm, \
    ElectronicCertificateForm, ResumeForm, AdditionalEducationCreateForm, ElectronicCertificateCreateForm, \
    InstitutionCreateForm, InstitutionForm
from app_resume.mixins import ResumeValidatorMixin, ResumeBounderMixin
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, ElectronicCertificate
from app_users.models import Profile, SocialLinks


# Create your views here.
class ResumeView(TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, username, slug, **kwargs):
        context = super().get_context_data(**kwargs)

        user = User.objects.get(username=username)
        context['user'] = user

        profile = Profile.objects.get(user=user)
        context['profile'] = profile

        resume = Resume.objects.get(slug=slug, profile=profile)
        context['resume'] = resume

        resume_about_me_form = ResumeAboutMeForm()
        context['resume_about_me_form'] = resume_about_me_form

        resume_soft_skills_form = ResumeSoftSkillsForm()
        context['resume_soft_skills_form'] = resume_soft_skills_form

        social_links = SocialLinks.objects.filter(profile=profile).first()
        context['social_links'] = social_links

        main_education = MainEducation.objects.filter(resume=resume).first()
        context['main_education'] = main_education

        main_education_form = MainEducationForm()
        context['main_education_form'] = main_education_form

        institutions = Institution.objects.filter(main_education=main_education)
        context['institutions'] = institutions

        context['institution_forms'] = {}
        for institution in institutions:
            institution_form = InstitutionForm(instance=institution)
            context['institution_forms'][institution] = institution_form

        institution_create_form = InstitutionCreateForm()
        context['institution_create_form'] = institution_create_form

        additional_educations = AdditionalEducation.objects.filter(resume=resume)
        context['additional_educations'] = additional_educations

        context['additional_education_forms'] = {}
        for education in additional_educations:
            additional_education_form = AdditionalEducationForm(instance=education)
            context['additional_education_forms'][education] = additional_education_form

        additional_education_create_form = AdditionalEducationCreateForm()
        context['additional_education_create_form'] = additional_education_create_form

        electronic_certificates = ElectronicCertificate.objects.filter(resume=resume)
        context['electronic_certificates'] = electronic_certificates

        context['electronic_certificate_forms'] = {}
        for certificate in electronic_certificates:
            electronic_certificate_form = ElectronicCertificateForm(instance=certificate)
            context['electronic_certificate_forms'][certificate] = electronic_certificate_form

        electronic_certificate_create_form = ElectronicCertificateCreateForm()
        context['electronic_certificate_create_form'] = electronic_certificate_create_form

        breadcrumbs = [
            ('Резюме', 'resume/'),
            (user.username, '#'),
            (resume.position, ''.join(['resume/', username, '-', slug, '/'])),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class ResumeAboutMeUpdateView(ResumeValidatorMixin, UpdateView):
    model = Resume
    fields = ['about_me']


class ResumeSoftSkillsUpdateView(ResumeValidatorMixin, UpdateView):
    model = Resume
    fields = ['soft_skills']


class MainEducationCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    form_class = MainEducationForm


class InstitutionCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = Institution
    fields = ['title']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        main_education = MainEducation.objects.get(resume=resume)
        self.object.main_education = main_education

        super()
        return super().form_valid(form)


class InstitutionUpdateView(ResumeBounderMixin, ResumeValidatorMixin, UpdateView):
    model = Institution
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        main_education = MainEducation.objects.get(resume=resume)
        self.object.main_education = main_education

        super()
        return super().form_valid(form)


class AdditionalEducationCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = AdditionalEducation
    fields = ['title']


class AdditionalEducationUpdateView(ResumeBounderMixin, ResumeValidatorMixin, UpdateView):
    model = AdditionalEducation
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        main_education = MainEducation.objects.get(resume=resume)
        self.object.main_education = main_education

        super()
        return super().form_valid(form)


class ElectronicCertificateCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = ElectronicCertificate
    fields = ['title']


class ElectronicCertificateUpdateView(ResumeBounderMixin, ResumeValidatorMixin, UpdateView):
    model = ElectronicCertificate
    fields = ['title', 'certificate_url', 'certificate', 'completion_percentage', 'completion_date']
