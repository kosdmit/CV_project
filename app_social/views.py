import json

from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView, ListView

from CV_project.settings import RATING_SETTINGS
from app_resume.mixins import remove_parameters_from_url
from app_resume.models import Resume
from app_social.forms import CommentForm, CommentUpdateForm
from app_social.mixins import OpenCommentModalIfSuccess, \
    AddLikesIntoContextMixin, get_resume_by_element_uuid
from app_social.models import Like, Comment


# Create your views here.
class ClickLike(View):
    def post(self, form):
        request_body_data = json.loads(self.request.body.decode('utf-8'))

        existing_like = Like.objects.filter(user=self.request.user, uuid_key=request_body_data['pk']).first()
        likes_count = Like.objects.filter(uuid_key=request_body_data['pk']).count()

        resume = get_resume_by_element_uuid(request_body_data['pk'])

        if existing_like:
            existing_like.delete()
            resume.rating -= RATING_SETTINGS['like']
            resume.save()
            return JsonResponse({'is_liked': False,
                                 'likes_count': likes_count-1})
        else:
            like = Like(user=self.request.user, uuid_key=request_body_data['pk'])
            like.save()
            resume.rating += RATING_SETTINGS['like']
            resume.save()
            return JsonResponse({'is_liked': True,
                                 'likes_count': likes_count+1})


class CommentCreateView(OpenCommentModalIfSuccess, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.uuid_key = self.kwargs['pk']
        self.object.is_approved = True

        resume = get_resume_by_element_uuid(self.kwargs['pk'])
        resume.rating += RATING_SETTINGS['comment']
        resume.save()

        return super().form_valid(form)


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def form_valid(self, form):
        resume = get_resume_by_element_uuid(self.object.uuid_key)
        resume.rating -= RATING_SETTINGS['comment']
        resume.save()

        return super().form_valid(form)


class CommentUpdateView(OpenCommentModalIfSuccess, UpdateView):
    model = Comment
    fields = ['message']


class ResumeListView(AddLikesIntoContextMixin, ListView):
    template_name = 'app_social/resume_list.html'
    model = Resume
    paginate_by = 5
    ordering = '-rating'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        comment_form = CommentForm()
        context['comment_form'] = comment_form

        uuid_with_comments = Comment.objects.filter(uuid_key__in=Resume.objects.values('pk'))\
            .values_list('uuid_key', flat=True).distinct()

        comments = {}
        comment_edit_forms = {}
        for uuid_key in uuid_with_comments:
            comments[uuid_key] = Comment.objects.filter(uuid_key=uuid_key)
            for comment in comments[uuid_key]:
                comment_edit_forms[comment.pk] = CommentUpdateForm(
                    instance=comment)
        context['comments'] = comments
        context['comment_edit_forms'] = comment_edit_forms

        comment_counts_result = Comment.objects.values('uuid_key') \
            .order_by('uuid_key') \
            .annotate(count=Count('uuid_key'))
        comment_counts = {}
        for dict in comment_counts_result:
            comment_counts[dict['uuid_key']] = dict['count']
        context['comment_counts'] = comment_counts

        if self.search_query:
            title = 'Поиск по резюме'
        else:
            title = 'Обзор'
        context['title'] = title

        return context

    def get_queryset(self):
        self.search_query = self.request.GET.get('search_query')
        if self.search_query:
            query_set = Resume.objects.filter(position__icontains=self.search_query)
            return query_set
        else:
            return super().get_queryset()




