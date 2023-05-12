import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import CreateView

from app_social.models import Like


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




