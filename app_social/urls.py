from django.urls import path

from app_social.views import ClickLike, CommentCreateView

urlpatterns = [
    path('click_like', ClickLike.as_view(), name='click_like'),
    path('comment_create/<pk>/', CommentCreateView.as_view(), name='comment_create'),

]