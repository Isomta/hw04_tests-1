from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import func_paginator


#@cache_page(60 * 15)
def index(request):
    posts_list = Post.objects.select_related('group', 'author').all()
    page_obj = func_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


#@cache_page(60 * 15)
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('author').all()
    page_obj = func_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    person = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=person,
        ).exists()
        followings = Follow.objects.filter(user=request.user).count()
        followers = Follow.objects.filter(author=request.user).count()
    posts = person.posts.select_related('group').all()
    page_obj = func_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'author': person,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.select_related('author').all()
    context = {'post': post, 'form': form, 'comments': comments,}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post.id)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    post.delete()
    return redirect('posts:profile', request.user.username)

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts_list = (
        Post.objects.prefetch_related('author')
        .prefetch_related('author__following')
        .filter(author__following__user=request.user)
    )
    page_obj = func_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)

@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if user == author:
        return redirect('posts:index')
    Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:follow_index')

@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:index')
