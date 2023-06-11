from django.urls import path

from app_social.views import ClickLike, CommentCreateView, CommentDeleteView, \
    CommentUpdateView, ResumeListView, PostCreateView, PostDeleteView, PostUpdateView, PostListView

urlpatterns = [
    path('click_like', ClickLike.as_view(), name='click_like'),
    path('resume_list', ResumeListView.as_view(), name='resume_list'),
    path('post_list', PostListView.as_view(), name='post_list'),

    #Comment items
    path('comment_create/<pk>/', CommentCreateView.as_view(), name='comment_create'),
    path('comment_delete/<pk>/', CommentDeleteView.as_view(), name='comment_delete'),
    path('comment_update/<pk>/', CommentUpdateView.as_view(), name='comment_update'),

    #Post items
    path('<username>/<slug>/post_create/', PostCreateView.as_view(), name='post_create'),
    path('<username>/<slug>/<pk>/post_delete/', PostDeleteView.as_view(), name='post_delete'),
    path('<username>/<slug>/<pk>/post_update/', PostUpdateView.as_view(), name='post_update'),

]