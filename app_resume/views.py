from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView, UpdateView

from app_resume.forms import ResumeForm, MainEducationForm, AdditionalEducationForm, ElectronicCertificateForm
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, ElectronicCertificate
from app_users.models import Profile, SocialLinks


# Create your views here.
class ResumeView(TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, username, slug, **kwargs):
        context = super().get_context_data(**kwargs)

        resume = Resume.objects.get(slug=slug)
        context['resume'] = Resume.objects.get(slug=slug)

        resume_form = ResumeForm()
        context['resume_form'] = resume_form

        user = User.objects.get(username=username)
        context['user'] = user

        profile = Profile.objects.get(user=user)
        context['profile'] = profile

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

        additional_education_form = AdditionalEducationForm()
        context['additional_educations_form'] = additional_education_form

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


class ResumeUpdateView(UpdateView):
    pass


