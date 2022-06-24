from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import func_paginator


def index(request):
    posts_list = Post.objects.select_related('group', 'author').all()
    page_obj = func_paginator(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


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
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=person,
        ).exists()
    posts = person.posts.select_related('group').all()
    page_obj = func_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'author': person,
        'following' : following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.select_related('author', 'group').get(id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = {'post': post, 'form': form, 'comments': comments}
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
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user and request.user != comment.post.author:
        return redirect('posts:post_detail', post_id=comment.post.id)
    comment.delete()
    return redirect('posts:post_detail', post_id=comment.post.id)


@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    comments = post.comments.select_related('author').all()
    if comment.author != request.user:
        return redirect('posts:post_detail', post_id=comment.post.id)
    form = CommentForm(
        request.POST or None,
        instance=comment,
    )
    if not form.is_valid():
        context = {'post': post, 'form': form, 'comments': comments}
        return render(request, 'posts/post_detail.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=comment.post.id)


@login_required
def follow_index(request):
    posts_list = Post.objects.select_related(
        'author', 'group'
    ).filter(author__following__user=request.user)
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
        return redirect('posts:profile', username)
    Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(user=request.user, author__username=username).delete()
    return redirect('posts:profile', username)
