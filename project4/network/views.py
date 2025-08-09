from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post
import json
from django.views.decorators.http import require_http_methods
from .models import Comment
from django.db.models import Prefetch 

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')  
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def index(request):
    """Render the main index page"""
    return render(request, "network/index.html")

@login_required
def new_post(request):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content", "")
        if content:
            post = Post(user=request.user, content=content)
            post.save()
            return JsonResponse({"message": "Post created successfully."}, status=201)
        return JsonResponse({"error": "Content cannot be empty."}, status=400)
    return JsonResponse({"error": "POST request required."}, status=400)

def posts(request, type_posts="all", username=None):
    if type_posts == "all":
        posts = Post.objects.all()
    elif type_posts == "following":
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=400)
        following = request.user.following.all()
        posts = Post.objects.filter(user__in=following)
    elif type_posts == "profile":
        user = get_object_or_404(User, username=username)
        posts = user.posts.all()
    else:
        return JsonResponse({"error": "Invalid posts type."}, status=400)
    
    posts = posts.order_by("-timestamp").all()
    page_number = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(page_number)
    
    return JsonResponse({
        "posts": [post.serialize(request.user) for post in page_obj],
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous()
    }, safe=False)

def profile(request, username):
    user = get_object_or_404(User, username=username)
    
    if request.method == "PUT":
        data = json.loads(request.body)
        action = data.get("action", "")
        if action == "follow":
            request.user.following.add(user)
        elif action == "unfollow":
            request.user.following.remove(user)
        return JsonResponse({"message": "Success."}, status=200)
    
    
    return render(request, "network/profile.html", {
        "profile_user": user,
        "is_following": request.user.is_authenticated and 
                       request.user != user and 
                       request.user.following.filter(pk=user.pk).exists()
    })
@login_required
@csrf_exempt
def edit_post(request, post_id):
    if request.method == "PUT":
        post = get_object_or_404(Post, pk=post_id)
        if post.user != request.user:
            return JsonResponse({"error": "You can't edit this post."}, status=403)
        data = json.loads(request.body)
        post.content = data.get("content", post.content)
        post.save()
        return JsonResponse({"message": "Post updated successfully."}, status=200)
    return JsonResponse({"error": "PUT request required."}, status=400)

@login_required(login_url='/login')  
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, pk=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({
            "message": "Success.",
            "liked": liked,
            "likes_count": post.likes.count()
        }, status=200)
    return JsonResponse({"error": "POST request required."}, status=400)

@login_required
def follow(request, user_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            target_user = User.objects.get(pk=user_id)
            
            if data.get('action') == 'follow':
                request.user.following.add(target_user)
            else:
                request.user.following.remove(target_user)
                
            return JsonResponse({
                'success': True,
                'followers_count': target_user.followers.count(),
                'action': data.get('action')
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def profile_posts(request, username):
    if request.method == 'GET':
        
        page_number = request.GET.get('page', 1)

        user = User.objects.get(username=username)
        posts = Post.objects.filter(user=user).order_by('-timestamp')

        paginator = Paginator(posts, 10)
        page_obj = paginator.get_page(page_number)
        
        posts_data = []
        for post in page_obj:
            posts_data.append({
                'id': post.id,
                'user': post.user.username,
                'content': post.content,
                'timestamp': post.timestamp.strftime("%b %d %Y, %I:%M %p"),
                'likes': post.likes.count()
            })
        
        return JsonResponse({
            'posts': posts_data,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages
        })
@login_required
def following(request):
    following_users = request.user.following.all()
    posts = Post.objects.filter(user__in=following_users).order_by('-timestamp')
    return render(request, 'network/following.html', {
        'posts': posts
    })
    
def profile_posts(request, username):
    if request.method == 'GET':
        try:
            profile_user = User.objects.get(username=username)
            posts = Post.objects.filter(user=profile_user).order_by('-timestamp')
            page_number = request.GET.get('page', 1)
            paginator = Paginator(posts, 10)  
            page_obj = paginator.get_page(page_number)

            posts_data = []
            for post in page_obj:
                posts_data.append({
                    'id': post.id,
                    'username': post.user.username,
                    'content': post.content,
                    'timestamp': post.timestamp.strftime("%b %d %Y, %I:%M %p"),
                    'likes': post.likes.count(),
                    'liked': request.user.is_authenticated and request.user in post.likes.all()
                })
            
            return JsonResponse({
                'posts': posts_data,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

@require_http_methods(["POST"])
def add_comment(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to comment."}, status=403)
    
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)
    
    data = json.loads(request.body)
    content = data.get("content", "").strip()
    
    if not content:
        return JsonResponse({"error": "Comment cannot be empty."}, status=400)
    
    comment = Comment.objects.create(
        user=request.user,
        post=post,
        content=content
    )
    
    return JsonResponse({
        "message": "Comment added successfully.",
        "comment": comment.serialize(request.user)
    })

@require_http_methods(["DELETE"])
def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to delete comments."}, status=403)
    
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Comment not found."}, status=404)
    
    if comment.user != request.user:
        return JsonResponse({"error": "You can only delete your own comments."}, status=403)
    
    comment.delete()
    return JsonResponse({"message": "Comment deleted successfully."})
    
def get_posts(request, type, username=None):
    page = request.GET.get('page', 1)
    
    if type == 'all':
        posts = Post.objects.all()
    elif type == 'following':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        following = request.user.following.all()
        posts = Post.objects.filter(user__in=following)
    elif type == 'user':
        try:
            user = User.objects.get(username=username)
            posts = Post.objects.filter(user=user)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid post type'}, status=400)
    
    
    posts = posts.order_by('-timestamp').prefetch_related(
        'likes'),
    Prefetch('comments', queryset=Comment.objects.select_related('user').order_by('-timestamp'))
    
    paginator = Paginator(posts, 10)
    try:
        posts_page = paginator.page(page)
    except EmptyPage:
        return JsonResponse({'error': 'Page not found'}, status=404)
    
    return JsonResponse({
        'posts': [post.serialize(request.user) for post in posts_page],
        'has_previous': posts_page.has_previous(),
        'has_next': posts_page.has_next()
    })
