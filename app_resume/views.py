from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, AdditionalEducationForm, \
    ElectronicCertificateForm, ResumeForm, AdditionalEducationCreateForm
from app_resume.mixins import ResumeValidatorMixin
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

        additional_educations = AdditionalEducation.objects.filter(resume=resume)
        context['additional_educations'] = additional_educations

        additional_education_create_form = AdditionalEducationCreateForm()
        context['additional_education_create_form'] = additional_education_create_form

        electronic_certificates = ElectronicCertificate.objects.filter(resume=resume)
        context['electronic_certificates'] = electronic_certificates

        electronic_certificate_form = ElectronicCertificateForm()
        context['electronic_certificate_form'] = electronic_certificate_form

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


class MainEducationCreateView(ResumeValidatorMixin, CreateView):
    form_class = MainEducationForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        self.object.resume = resume
        self.object.save()

        return super().form_valid(form)


class AdditionalEducationCreateView(ResumeValidatorMixin, CreateView):
    model = AdditionalEducation
    fields = ['title']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        self.object.resume = resume
        self.object.save()

        return super().form_valid(form)