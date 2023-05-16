from django.urls import path

from app_social.views import ClickLike, CommentCreateView, CommentDeleteView, \
    CommentUpdateView

urlpatterns = [
    path('click_like', ClickLike.as_view(), name='click_like'),
    path('comment_create/<pk>/', CommentCreateView.as_view(), name='comment_create'),
    path('comment_delete/<pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comment_update/<pk>/', CommentUpdateView.as_view(), name='comment_update'),

]