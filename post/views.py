import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render

from .models import Post

logger = logging.getLogger(__name__)


def post_list(request):
    """Public news/announcements feed — no login required.

    Renders templates/news_list.html, which supports free-text search
    (?q=) and category filtering (?category=announcement|update|alert|scheme).
    """
    posts_list = Post.objects.filter(is_published=True)

    search_query = request.GET.get("q", "").strip()
    if search_query:
        posts_list = posts_list.filter(title__icontains=search_query)

    category = request.GET.get("category", "").strip()
    if category:
        posts_list = posts_list.filter(category=category)

    paginator = Paginator(posts_list, 10)
    page = request.GET.get("page")
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "news_list.html",
        {"posts": posts, "search_query": search_query, "category": category},
    )


def post_detail(request, pk):
    """Public single-article view — no login required."""
    post = get_object_or_404(Post, pk=pk, is_published=True)
    return render(request, "post.html", {"post": post})
