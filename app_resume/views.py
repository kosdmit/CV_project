from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView, DeleteView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, AdditionalEducationForm, \
    ElectronicCertificateForm, ResumeForm, AdditionalEducationCreateForm, ElectronicCertificateCreateForm, \
    InstitutionCreateForm, InstitutionForm, SkillCreateForm, WorkExpSectionForm, JobCreateForm, JobForm, \
    ResumePositionForm
from app_resume.mixins import ResumeValidatorMixin, ResumeBounderMixin
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, ElectronicCertificate, Skill, \
    WorkExpSection, Job
from app_users.forms import SocialLinksForm
from app_users.models import Profile, SocialLinks


# Create your views here.
class MainView(RedirectView):
    USER_TO_REDIRECT = 'kosdmit'

    if Resume.objects.filter(user__username=USER_TO_REDIRECT, is_primary=True).first():
        url_to_redirect = reverse_lazy('primary_resume', kwargs={'username': USER_TO_REDIRECT})
    else:
        url_to_redirect = reverse_lazy('login')

    url = url_to_redirect


class ResumeView(TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        owner = User.objects.get(username=kwargs['username'])
        if self.request.user.is_authenticated:
            context['owner'] = owner

        profile = Profile.objects.get(user=owner)
        context['profile'] = profile

        try:
            slug = kwargs['slug']
            resume = Resume.objects.get(slug=slug, profile=profile)
        except KeyError:
            slug = ''
            resume = Resume.objects.get(profile=profile, is_primary=True)
        context['resume'] = resume

        resume_position_form = ResumePositionForm(instance=resume)
        context['resume_position_form'] = resume_position_form

        resume_about_me_form = ResumeAboutMeForm()
        context['resume_about_me_form'] = resume_about_me_form

        resume_soft_skills_form = ResumeSoftSkillsForm()
        context['resume_soft_skills_form'] = resume_soft_skills_form

        social_links = SocialLinks.objects.filter(profile=profile).first()
        context['social_links'] = social_links

        social_links_form = SocialLinksForm(instance=social_links)
        context['social_links_form'] = social_links_form

        main_education = MainEducation.objects.filter(resume=resume).first()
        context['main_education'] = main_education

        main_education_form = MainEducationForm(instance=main_education)
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
            electronic_certificate_form = ElectronicCertificateForm(
                instance=certificate,
                auto_id=f"id_%s_{certificate.pk}"
            )
            context['electronic_certificate_forms'][certificate] = electronic_certificate_form

        electronic_certificate_create_form = ElectronicCertificateCreateForm()
        context['electronic_certificate_create_form'] = electronic_certificate_create_form

        skills = Skill.objects.filter(resume=resume)
        context['skills'] = skills

        skill_create_form = SkillCreateForm()
        context['skill_create_form'] = skill_create_form

        work_exp_sections = WorkExpSection.objects.filter(resume=resume)
        context['work_exp_sections'] = work_exp_sections

        work_exp_section_form = WorkExpSectionForm()
        context['work_exp_section_form'] = work_exp_section_form

        context['work_exp_section_update_forms'] = {}
        for section in work_exp_sections:
            work_exp_section_update_form = WorkExpSectionForm(
                instance=section,
                auto_id=f"id_%s_{section.pk}"
            )
            context['work_exp_section_update_forms'][section] = work_exp_section_update_form

        context['jobs_in_sections'] = {}
        for section in work_exp_sections:
            jobs = Job.objects.filter(work_exp_section=section)
            job_form_dicts = []
            for job in jobs:
                job_update_form = JobForm(instance=job)
                job_form_dicts.append({'job': job,
                                       'job_update_form': job_update_form})
            context['jobs_in_sections'][section] = job_form_dicts

        job_create_form = JobCreateForm()
        context['job_create_form'] = job_create_form


        breadcrumbs = [
            ('Резюме', 'resume/'),
            (owner.username, '#'),
            (resume.position, ''.join(['resume/', kwargs['username'], '-', slug, '/'])),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context


class ResumePositionUpdateView(ResumeValidatorMixin, UpdateView):
    model = Resume
    fields = ['position']


class ResumeAboutMeUpdateView(ResumeValidatorMixin, UpdateView):
    model = Resume
    fields = ['about_me']


class ResumeSoftSkillsUpdateView(ResumeValidatorMixin, UpdateView):
    model = Resume
    fields = ['soft_skills']


class ResumeIsPrimaryUpdateView(UpdateView):
    model = Resume
    fields = ['is_primary']
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        obj = Resume.objects.get(pk=self.request.POST['is_primary'])
        return obj


class MainEducationCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    form_class = MainEducationForm


class MainEducationUpdateView(UpdateView):
    form_class = MainEducationForm
    model = MainEducation

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


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


class InstitutionDeleteView(DeleteView):
    model = Institution

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class AdditionalEducationCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = AdditionalEducation
    fields = ['title']


class AdditionalEducationDeleteView(DeleteView):
    model = AdditionalEducation

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


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


class ElectronicCertificateDeleteView(DeleteView):
    model = ElectronicCertificate

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class SkillCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = Skill
    fields = ['name']


class SkillDeleteView(DeleteView):
    model = Skill

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class WorkExpSectionCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    form_class = WorkExpSectionForm


class WorkExpSectionUpdateView(UpdateView):
    form_class = WorkExpSectionForm
    model = WorkExpSection

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class WorkExpSectionDeleteView(DeleteView):
    model = WorkExpSection

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class JobCreateView(ResumeBounderMixin, ResumeValidatorMixin, CreateView):
    model = Job
    fields = ['title']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        work_exp_section = WorkExpSection.objects.get(pk=self.kwargs['section'])
        self.object.work_exp_section = work_exp_section

        super()
        return super().form_valid(form)


class JobUpdateView(ResumeBounderMixin, ResumeValidatorMixin, UpdateView):
    form_class = JobForm
    model = Job


class JobDeleteView(DeleteView):
    model = Job

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


