from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.posts, name="posts"),
    path("posts/<str:type_posts>", views.posts, name="posts_type"),
    path("posts/user/<str:username>", views.posts, name="user_posts"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("post", views.new_post, name="new_post"),
    path("post/<int:post_id>", views.edit_post, name="edit_post"),
    path("like/<int:post_id>", views.like_post, name="like_post"),
    path('profile_posts/<str:username>', views.profile_posts, name='profile_posts'),
    path('follow/<int:user_id>', views.follow, name='follow'),
    path('following', views.following, name='following'),
    path('profile_posts/<str:username>', views.profile_posts, name='profile_posts'),
    path('posts/<str:type>', views.get_posts, name='get_posts'),
    path('posts/user/<str:username>', views.get_posts, {'type': 'user'}, name='user_posts'),
    path('post/<int:post_id>/comment', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>', views.delete_comment, name='delete_comment'),
]
