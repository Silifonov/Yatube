from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from .utils import paginator
from .models import (
    Post,
    Group,
    Follow
)
from .forms import (
    PostForm,
    CommentForm
)
from .const import (
    INDEX_TEMPLATE,
    GROUP_LIST_TEMPLATE,
    PROFILE_TEMPLATE,
    POST_DETAIL_TEMPLATE,
    POST_CREATE_TEMPLATE,
    FOLLOW_INDEX_TEMPLATE,

    PROFILE_URL_NAME,
    POST_DETAIL_URL_NAME,
)

User = get_user_model()


@cache_page(20)
def index(request):
    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, INDEX_TEMPLATE, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = paginator(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, GROUP_LIST_TEMPLATE, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').all()
    if request.user.is_authenticated:
        try:
            following = Follow.objects.get(
                user=request.user, author=author)
        except ObjectDoesNotExist:
            following = False
    else:
        following = False
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
        'following': following,
        'author': author
    }
    return render(request, PROFILE_TEMPLATE, context)


def post_detail(request, post_id):
    post = Post.objects.select_related('author', 'group').get(id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    posts_count = post.author.posts.count()
    context = {
        'post': post,
        'posts_count': posts_count,
        'form': form,
        'comments': comments
    }
    return render(request, POST_DETAIL_TEMPLATE, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(PROFILE_URL_NAME, request.user.username)
    return render(request, POST_CREATE_TEMPLATE, context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.select_related('author', 'group').get(id=post_id)
    if post.author != request.user:
        return redirect(POST_DETAIL_URL_NAME, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'is_edit': True
    }
    if form.is_valid():
        form.save()
        return redirect(POST_DETAIL_URL_NAME, post_id)
    return render(request, POST_CREATE_TEMPLATE, context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(POST_DETAIL_URL_NAME, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, FOLLOW_INDEX_TEMPLATE, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect(PROFILE_URL_NAME, username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect(PROFILE_URL_NAME, username)
