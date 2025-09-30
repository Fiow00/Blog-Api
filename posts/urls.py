from django.urls import path

from .views import *

urlpatterns = [
    path("posts/<int:pk>/", PostDetail.as_view(), name="post_detail"),
    path("posts/", PostList.as_view(), name="post_list"),
]