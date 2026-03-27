from django.shortcuts import render
from .models import Post
from django.contrib.auth.decorators import login_required

# NEWS SECTION
@login_required
def news_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'news_list.html', {'posts': posts})

@login_required
def news_detail(request, id):
    post = Post.objects.get(id=id)
    return render(request, 'post.html', {'post': post})
