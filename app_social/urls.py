from django.urls import path

from app_social.views import ClickLike

urlpatterns = [
    path('click_like', ClickLike.as_view(), name='click_like'),

]