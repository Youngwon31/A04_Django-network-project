from django.shortcuts import render
from .models import Post
from django.http import JsonResponse
from django.core import serializers
from .forms import PostForm
from profiles.models import Profile

# Create your views here.


def post_list_and_create(request):
    form = PostForm(request.POST or None)
    # qs = Post.objects.all()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if form.is_valid():
            author = Profile.objects.get(user=request.user)
            isinstance = form.save(commit=False)
            isinstance.author = author
            isinstance.save()
            return JsonResponse({
                'title': isinstance.title,
                'body': isinstance.body,
                'author': isinstance.author.user.username,
                'id': isinstance.id,
            })

    context = {
        'form': form,
    }
    return render(request, 'posts/main.html', context)


def post_detail(request, pk):
    obj = Post.objects.get(pk=pk)
    form = PostForm()

    context = {
        'obj': obj,
        'form': form,
    }

    return render(request, 'posts/detail.html', context)


def load_post_data_view(request, num_posts):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        visiable = 3
        upper = num_posts  # 9
        lower = upper - visiable  # 6
        size = Post.objects.all().count()

        qs = Post.objects.all()
        data = []
        for obj in qs:
            item = {
                'id': obj.id,
                'title': obj.title,
                'body': obj.body,
                'liked': True if request.user in obj.liked.all() else False,
                'count': obj.like_count,
                'authour': obj.author.user.username
            }
            data.append(item)
        # data = serializers.serialize('json', qs)
        return JsonResponse({'data': data[lower:upper], 'size': size})


def post_detail_data_view(request, pk):
    obj = Post.objects.get(pk=pk)

    data = {
        'id': obj.id,
        'title': obj.title,
        'body': obj.body,
        'author': obj.author.user.username,
        'logged_in': request.user.username,
    }

    return JsonResponse({'data': data})


def like_unlike_post(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pk = request.POST.get('pk')
        obj = Post.objects.get(pk=pk)
        if request.user in obj.liked.all():
            liked = False
            obj.liked.remove(request.user)
        else:
            liked = True
            obj.liked.add(request.user)
        return JsonResponse({'liked': liked, 'count': obj.like_count})


def update_post(request, pk):
    obj = Post.objects.get(pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_title = request.POST.get('title')
        new_body = request.POST.get('body')
        obj.title = new_title
        obj.body = new_body
        obj.save()
        return JsonResponse({
            'title': new_title,
            'body': new_body,
        })


def delete_post(request, pk):
    obj = Post.objects.get(pk=pk)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        obj.delete()
        return JsonResponse({})
