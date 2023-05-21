from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, RedirectView, DeleteView

from app_resume.forms import ResumeAboutMeForm, ResumeSoftSkillsForm, MainEducationForm, AdditionalEducationForm, \
    ElectronicCertificateForm, AdditionalEducationCreateForm, ElectronicCertificateCreateForm, \
    InstitutionCreateForm, InstitutionForm, SkillCreateForm, WorkExpSectionForm, JobCreateForm, JobForm, \
    ResumePositionForm
from app_resume.mixins import ResumeValidatorMixin, ResumeBounderMixin, \
    OpenModalIfSuccessMixin, \
    RatingUpdateForCreateViewMixin, RatingUpdateForDeleteViewMixin
from app_resume.models import Resume, MainEducation, Institution, AdditionalEducation, ElectronicCertificate, Skill, \
    WorkExpSection, Job
from app_social.forms import CommentForm, CommentUpdateForm
from app_social.mixins import AddLikesIntoContextMixin
from app_social.models import Comment
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


class ResumeView(AddLikesIntoContextMixin, TemplateView):
    template_name = 'app_resume/resume.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        owner = User.objects.get(username=kwargs['username'])
        context['owner'] = owner

        try:
            slug = kwargs['slug']
            resume = Resume.objects.get(slug=slug, profile=owner.profile)
        except KeyError:
            resume = Resume.objects.get(profile=owner.profile, is_primary=True)
        context['resume'] = resume

        try:
            main_education = resume.maineducation
        except MainEducation.DoesNotExist:
            main_education = None

        if self.request.user.is_authenticated and self.request.user == owner:
            context = self.add_owners_forms(context, owner, resume, main_education)

        context['jobs_in_sections'] = {}
        for section in resume.workexpsection_set.all():
            jobs = Job.objects.filter(work_exp_section=section)
            job_form_dicts = []
            for job in jobs:
                if self.request.user == owner:
                    job_update_form = JobForm(instance=job)
                    job_form_dicts.append({'job': job,
                                           'job_update_form': job_update_form})
                else:
                    job_form_dicts.append({'job': job})

            context['jobs_in_sections'][section] = job_form_dicts

        uuid_with_comments = Comment.objects.filter(
            user__resume__id=resume.pk) \
            .values_list('uuid_key', flat=True).distinct()

        comments = {}
        comment_edit_forms = {}
        for uuid_key in uuid_with_comments:
            comments[uuid_key] = Comment.objects.filter(uuid_key=uuid_key)
            for comment in comments[uuid_key]:
                if comment.user == self.request.user:
                    comment_edit_forms[comment.pk] = CommentUpdateForm(
                        instance=comment)
        context['comments'] = comments
        context['comment_edit_forms'] = comment_edit_forms

        context['comment_form'] = CommentForm()

        comment_counts_result = Comment.objects.values('uuid_key') \
            .order_by('uuid_key') \
            .annotate(count=Count('uuid_key'))
        comment_counts = {}
        for dict in comment_counts_result:
            comment_counts[dict['uuid_key']] = dict['count']
        context['comment_counts'] = comment_counts

        breadcrumbs = [
            (owner.username, '/users/profile/'),
            (resume.position, ''),
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    @staticmethod
    def add_owners_forms(context, owner, resume, main_education):
        owners_forms = {
            'resume_position_form': ResumePositionForm(instance=resume),
            'resume_about_me_form': ResumeAboutMeForm(instance=resume),
            'resume_soft_skills_form': ResumeSoftSkillsForm(instance=resume),
            'social_links_form': SocialLinksForm(instance=owner.profile.sociallinks),
            'main_education_form': MainEducationForm(instance=main_education),
            'additional_education_create_form': AdditionalEducationCreateForm(),
            'electronic_certificate_create_form': ElectronicCertificateCreateForm(),
            'skill_create_form': SkillCreateForm(),
            'work_exp_section_form': WorkExpSectionForm(),
            'job_create_form': JobCreateForm(),

        }

        context.update(owners_forms)

        if main_education:
            context['institution_forms'] = {}
            for institution in resume.maineducation.institution_set.all():
                institution_form = InstitutionForm(instance=institution)
                context['institution_forms'][institution] = institution_form

            context['institution_create_form'] = InstitutionCreateForm()

        context['additional_education_forms'] = {}
        for education in resume.additionaleducation_set.all():
            additional_education_form = AdditionalEducationForm(
                instance=education)
            context['additional_education_forms'][
                education] = additional_education_form

        context['electronic_certificate_forms'] = {}
        for certificate in resume.electroniccertificate_set.all():
            electronic_certificate_form = ElectronicCertificateForm(
                instance=certificate,
                auto_id=f"id_%s_{certificate.pk}"
            )
            context['electronic_certificate_forms'][
                certificate] = electronic_certificate_form

        context['work_exp_section_update_forms'] = {}
        for section in resume.workexpsection_set.all():
            work_exp_section_update_form = WorkExpSectionForm(
                instance=section,
                auto_id=f"id_%s_{section.pk}"
            )
            context['work_exp_section_update_forms'][
                section] = work_exp_section_update_form

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


class MainEducationCreateView(OpenModalIfSuccessMixin,
                              ResumeBounderMixin,
                              ResumeValidatorMixin,
                              RatingUpdateForCreateViewMixin,
                              CreateView):
    form_class = MainEducationForm


class MainEducationUpdateView(UpdateView):
    form_class = MainEducationForm
    model = MainEducation

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class InstitutionCreateView(OpenModalIfSuccessMixin,
                            ResumeBounderMixin,
                            ResumeValidatorMixin,
                            RatingUpdateForCreateViewMixin,
                            CreateView):
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
    fields = ['title', 'description', 'website_url', 'diploma', 'completion_date',
              'is_primary']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        resume = Resume.objects.get(user=self.request.user, slug=self.kwargs['slug'])
        main_education = MainEducation.objects.get(resume=resume)
        self.object.main_education = main_education

        super()
        return super().form_valid(form)


class InstitutionDeleteView(RatingUpdateForDeleteViewMixin, DeleteView):
    model = Institution

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class AdditionalEducationCreateView(OpenModalIfSuccessMixin,
                                    ResumeBounderMixin,
                                    ResumeValidatorMixin,
                                    RatingUpdateForCreateViewMixin,
                                    CreateView):
    model = AdditionalEducation
    fields = ['title']


class AdditionalEducationDeleteView(RatingUpdateForDeleteViewMixin, DeleteView):
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


class ElectronicCertificateCreateView(OpenModalIfSuccessMixin,
                                      ResumeBounderMixin,
                                      ResumeValidatorMixin,
                                      RatingUpdateForCreateViewMixin,
                                      CreateView):
    model = ElectronicCertificate
    fields = ['title']


class ElectronicCertificateUpdateView(ResumeBounderMixin, ResumeValidatorMixin, UpdateView):
    model = ElectronicCertificate
    fields = ['title', 'certificate_url', 'certificate', 'completion_percentage', 'completion_date']


class ElectronicCertificateDeleteView(RatingUpdateForDeleteViewMixin, DeleteView):
    model = ElectronicCertificate

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class SkillCreateView(ResumeBounderMixin,
                      ResumeValidatorMixin,
                      RatingUpdateForCreateViewMixin,
                      CreateView):
    model = Skill
    fields = ['name']


class SkillDeleteView(RatingUpdateForDeleteViewMixin, DeleteView):
    model = Skill

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class WorkExpSectionCreateView(OpenModalIfSuccessMixin,
                               ResumeBounderMixin,
                               ResumeValidatorMixin,
                               CreateView):
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


class JobCreateView(OpenModalIfSuccessMixin,
                    ResumeBounderMixin,
                    ResumeValidatorMixin,
                    RatingUpdateForCreateViewMixin,
                    CreateView):
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


class JobDeleteView(RatingUpdateForDeleteViewMixin, DeleteView):
    model = Job

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


