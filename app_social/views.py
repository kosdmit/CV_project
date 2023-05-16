import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView

from app_social.forms import CommentForm
from app_social.models import Like, Comment


# Create your views here.
class ClickLike(View):
    def post(self, form):
        request_body_data = json.loads(self.request.body.decode('utf-8'))

        existing_like = Like.objects.filter(user=self.request.user, uuid_key=request_body_data['pk']).first()
        likes_count = Like.objects.filter(uuid_key=request_body_data['pk']).count()

        if existing_like:
            existing_like.delete()
            return JsonResponse({'is_liked': False,
                                 'likes_count': likes_count-1})
        else:
            like = Like(user=self.request.user, uuid_key=request_body_data['pk'])
            like.save()
            return JsonResponse({'is_liked': True,
                                 'likes_count': likes_count+1})


class CommentCreateView(CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.uuid_key = self.kwargs['pk']
        self.object.is_approved = True

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class CommentDeleteView(DeleteView):
    model = Comment

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']


class CommentUpdateView(UpdateView):
    model = Comment
    fields = ['message']

    def get_success_url(self):
        return self.request.META['HTTP_REFERER']





