from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all().select_related('author', 'group',)
    paginator = Paginator(post_list, Post.TEN_ACTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Записи сообщества'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all().select_related('author', 'group')
    paginator = Paginator(post_list, Post.TEN_ACTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    post_f = author.posts.all()[:Post.FIRST_POST]
    paginator = Paginator(posts, Post.TEN_ACTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated and Follow.objects.filter(
        author=author,
        user=request.user
    ).exists():
        following = True
    else:
        following = False
    context = {
        'page_obj': page_obj,
        'posts': posts,
        'author': author,
        'post_f': post_f,
        'following': following
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    form = CommentForm(request.POST or None, instance=post)
    comments = Comment.objects.filter(post=post)
    context = {
        'post': post,
        'author': author,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if author != request.user:
        return redirect('posts:post_detail', post_id)

    template = 'posts/create_post.html'
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    is_edit = True
    context = {
        'form': form,
        'is_edit': is_edit,
    }

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, template, context)


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
    title = 'Вы на них подписаны'
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, Post.TEN_ACTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    template = 'posts:profile'
    if (
            request.user == author
            or Follow.objects.get_or_create(
                author=author,
                user=request.user
            )
    ):
        return redirect(template, username=username)
    Follow.objects.create(author=author, user=request.user)

    return redirect(template, username=username)


@login_required
def profile_unfollow(request, username):
    template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()
    return redirect(template, username=username)
