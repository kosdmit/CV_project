from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, AdditionalEducationForm, \
    ElectronicCertificateForm, ResumeForm
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


class ResumeAboutMeUpdateView(UpdateView):
    model = Resume
    fields = ['about_me']

    def post(self, request, username, slug, *args, **kwargs):
        profile = Profile.objects.get(user=self.request.user)

        self.object = Resume.objects.get(profile=profile, slug=slug)

        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """

        form = self.get_form()
        if form.is_valid():

            if not request.user.username == username:
                raise ValidationError(
                    message='Username in URL is not correct',
                    params={'your username': request.user.username,
                            'received username': username,
                            }
                )

            self.success_url = reverse_lazy('resume', kwargs={'username': username,
                                                              'slug': slug,
                                                              })

            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ResumeSoftSkillsUpdateView(UpdateView):
    model = Resume
    fields = ['soft_skills']

    def post(self, request, username, slug, *args, **kwargs):
        profile = Profile.objects.get(user=self.request.user)

        self.object = Resume.objects.get(profile=profile, slug=slug)

        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """

        form = self.get_form()
        if form.is_valid():

            if not request.user.username == username:
                raise ValidationError(
                    message='Username in URL is not correct',
                    params={'your username': request.user.username,
                            'received username': username,
                            }
                )

            self.success_url = reverse_lazy('resume', kwargs={'username': username,
                                                              'slug': slug,
                                                              })

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

