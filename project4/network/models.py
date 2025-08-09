from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')

    def serialize(self, request_user=None):
        return {
            "username": self.username,
            "followers_count": self.followers.count(),
            "following_count": self.following.count(),
            "is_following": request_user.is_authenticated and request_user != self and request_user.following.filter(pk=self.pk).exists() if request_user else False
        }

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"Post by {self.user.username} at {self.timestamp}"

    def serialize(self, user=None):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes.count(),
            "is_liked": user.is_authenticated and self.likes.filter(pk=user.pk).exists() if user else False,
            "can_edit": user == self.user if user else False,
            "can_comment": user.is_authenticated if user else False,
            "comments": [comment.serialize(user) for comment in self.comments.all().order_by('-timestamp')]
        }


    
def serialize(self, user=None):
    return {
        "id": self.id,
        "user": self.user.username,
        "content": self.content,
        "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        "likes": self.likes.count(),
        "is_liked": user.is_authenticated and self.likes.filter(pk=user.pk).exists() if user else False,
        "can_edit": user == self.user if user else False,
        "can_comment": user.is_authenticated if user else False,
        "comments": [comment.serialize(user) for comment in self.comments.all().order_by('-timestamp')]
    }
        

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comment by {self.user.username} on post {self.post.id}"

    def serialize(self, user=None):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "can_delete": user == self.user if user else False
        }