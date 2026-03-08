from django.shortcuts import render
from .models import Post

# NEWS SECTION

def news_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'news_list.html', {'posts': posts})

def news_detail(request, id):
    post = Post.objects.get(id=id)
    return render(request, 'post.html', {'post': post})
