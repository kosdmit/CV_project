import json

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView, ListView

from CV_project.settings import RATING_SETTINGS
from app_resume.mixins import ResumeBounderMixin, ResumeValidatorMixin, \
    RefreshIfSuccessMixin, \
    RatingUpdateForCreateViewMixin, RatingUpdateForDeleteViewMixin, \
    OpenModalIfSuccessMixin, Http404IfGetRequestMixin
from app_resume.models import Resume
from app_social.forms import CommentForm, CommentUpdateForm, PostForm
from app_social.mixins import OpenCommentModalIfSuccess, AddLikesIntoContextMixin,\
    get_resume_by_element_uuid, OwnerValidatorMixin
from app_social.models import Like, Comment, Post


# Create your views here.
class ClickLike(Http404IfGetRequestMixin, View):
    def post(self, form):
        request_body_data = json.loads(self.request.body.decode('utf-8'))

        if self.request.user.is_authenticated:
            existing_like = Like.objects.filter(owner_id=self.request.user.id,
                                                uuid_key=request_body_data[
                                                    'pk']).first()
        else:
            session_id = self.request.session.session_key
            if not session_id:
                self.request.session.save()
                session_id = self.request.session.session_key
            existing_like = Like.objects.filter(owner_id=session_id,
                                                uuid_key=request_body_data[
                                                    'pk']).first()

        likes_count = Like.objects.filter(
            uuid_key=request_body_data['pk']).count()

        resume = get_resume_by_element_uuid(request_body_data['pk'])

        if existing_like:
            existing_like.delete()
            if resume:
                resume.rating -= RATING_SETTINGS['like']
                resume.save()
            return JsonResponse({'is_liked': False,
                                 'likes_count': likes_count - 1})
        else:
            if self.request.user.is_authenticated:
                like = Like(owner_id=self.request.user.id,
                            uuid_key=request_body_data['pk'])
            else:
                like = Like(owner_id=self.request.session.session_key,
                            uuid_key=request_body_data['pk'])

            like.save()
            if resume:
                resume.rating += RATING_SETTINGS['like']
                resume.save()
            return JsonResponse({'is_liked': True,
                                 'likes_count': likes_count + 1})


class CommentCreateView(Http404IfGetRequestMixin,
                        OpenCommentModalIfSuccess,
                        CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.uuid_key = self.kwargs['pk']
        if self.request.user.is_authenticated:
            self.object.is_approved = True
            self.object.owner_id = self.request.user.pk
            self.object.user = self.request.user
        else:
            self.object.is_approved = False
            self.object.owner_id = self.request.session.session_key
            messages.info(self.request, f'Ваше сообщение появится после проверки администратором.'
                                        f' <a href="{reverse_lazy("signup")}">Зарегистрируйтесь</a>, чтобы сообщения появлялись сразу.')

        resume = get_resume_by_element_uuid(self.kwargs['pk'])
        resume.rating += RATING_SETTINGS['comment']
        resume.save()

        return super().form_valid(form)


class CommentDeleteView(Http404IfGetRequestMixin,
                        OpenCommentModalIfSuccess,
                        OwnerValidatorMixin,
                        DeleteView):
    model = Comment

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']

    def form_valid(self, form):
        if (self.request.user.is_authenticated and self.object.user == self.request.user) \
                or self.object.owner_id == self.request.session.session_key:
            resume = get_resume_by_element_uuid(self.object.uuid_key)
            resume.rating -= RATING_SETTINGS['comment']
            resume.save()

        return super().form_valid(form)


class CommentUpdateView(Http404IfGetRequestMixin,
                        OwnerValidatorMixin,
                        OpenCommentModalIfSuccess,
                        UpdateView):
    model = Comment
    fields = ['message']


class ResumeListView(AddLikesIntoContextMixin, ListView):
    template_name = 'app_social/resume_list.html'
    model = Resume
    paginate_by = 5
    ordering = '-rating'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['comment_form'] = CommentForm()

        uuid_with_comments = Comment.objects.filter(
            uuid_key__in=Resume.objects.values('pk')) \
            .values_list('uuid_key', flat=True).distinct()

        comments = {}
        comment_edit_forms = {}
        for uuid_key in uuid_with_comments:
            comments[uuid_key] = Comment.objects.filter(uuid_key=uuid_key,
                                                        is_approved=True)
            for comment in comments[uuid_key]:
                if comment.owner_id == self.request.user.pk or self.request.session.session_key:
                    comment_edit_forms[comment.pk] = CommentUpdateForm(
                        instance=comment)
        context['comments'] = comments
        context['comment_edit_forms'] = comment_edit_forms

        comment_counts_result = Comment.objects.filter(is_approved=True) \
            .values('uuid_key') \
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

        breadcrumbs = [
            ('Обзор', reverse_lazy('resume_list'))
        ]
        context['breadcrumbs'] = breadcrumbs

        return context

    def get_queryset(self):
        self.search_query = self.request.GET.get('search_query')
        if self.search_query:
            query_set = Resume.objects.filter(
                position__icontains=self.search_query)
            return query_set
        else:
            return super().get_queryset()


class PostCreateView(OpenModalIfSuccessMixin,
                     ResumeBounderMixin,
                     ResumeValidatorMixin,
                     RefreshIfSuccessMixin,
                     RatingUpdateForCreateViewMixin,
                     Http404IfGetRequestMixin,
                     CreateView):
    model = Post
    fields = ['message', 'image']


class PostUpdateView(ResumeValidatorMixin,
                     RefreshIfSuccessMixin,
                     Http404IfGetRequestMixin,
                     UpdateView):
    model = Post
    fields = ['message', 'image']


class PostDeleteView(ResumeValidatorMixin,
                     RefreshIfSuccessMixin,
                     RatingUpdateForDeleteViewMixin,
                     Http404IfGetRequestMixin,
                     DeleteView):
    model = Post


class PostListView(AddLikesIntoContextMixin, ListView):
    template_name = 'app_social/post_list.html'
    model = Post
    paginate_by = 8
    ordering = '-created_date'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['comment_form'] = CommentForm()

        uuid_with_comments = Comment.objects.filter(
            uuid_key__in=Post.objects.all()) \
            .values_list('uuid_key', flat=True).distinct()

        comments = {}
        comment_edit_forms = {}
        for uuid_key in uuid_with_comments:
            comments[uuid_key] = Comment.objects.filter(uuid_key=uuid_key,
                                                        is_approved=True)
            for comment in comments[uuid_key]:
                if comment.owner_id == self.request.user.pk or self.request.session.session_key:
                    comment_edit_forms[comment.pk] = CommentUpdateForm(
                        instance=comment)
        context['comments'] = comments
        context['comment_edit_forms'] = comment_edit_forms

        comment_counts_result = Comment.objects.filter(is_approved=True) \
            .values('uuid_key') \
            .order_by('uuid_key') \
            .annotate(count=Count('uuid_key'))
        comment_counts = {}
        for dict in comment_counts_result:
            comment_counts[dict['uuid_key']] = dict['count']
        context['comment_counts'] = comment_counts

        if self.username_search_query:
            title = f'Новости пользователя'
        else:
            title = 'Блоги'
        context['title'] = title

        breadcrumbs = [
            ('Блоги', reverse_lazy('post_list'))
        ]
        context['breadcrumbs'] = breadcrumbs

        context['post_update_forms'] = {}
        for post in context['page_obj']:
            if post.resume.user == self.request.user:
                post_update_form = PostForm(instance=post, auto_id=False)
                context['post_update_forms'][post] = post_update_form

        try:
            user = User.objects.get(username=self.username_search_query)
            context['author'] = user
        except User.DoesNotExist:
            pass

        return context

    def get_queryset(self):
        self.username_search_query = self.request.GET.get('username_search_query')
        self.slug_search_query = self.request.GET.get('slug_search_query')

        if self.username_search_query and self.slug_search_query:
            query_set = Post.objects.filter(
                resume__user__username=self.username_search_query,
                resume__slug=self.slug_search_query).order_by('-created_date')
            return query_set
        elif self.username_search_query:
            query_set = Post.objects.filter(
                resume__user__username=self.username_search_query).order_by('-created_date')
            return query_set
        else:
            return super().get_queryset()
