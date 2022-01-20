from .views import *
from django.urls import path, include


urlpatterns = [
    path('follow/<id>', follow, name="follow"),
    path('unfollow/<id>', unfollow, name="unfollow"),
    path('user', userprofile, name="user"),
    path('posts', addpost, name="posts"),
    path('posts/<id>', deletepost, name="posts"),
    path('like/<id>', likepost, name="like"),
    path('unlike/<id>', unlikepost, name="unlike"),
    path('comment/<id>', addcomment, name="comment"),
    path('all_posts', all_posts, name="all_posts"),
]