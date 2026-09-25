from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from core.throttle import throttle
from .forms import ReviewForm
from .models import Review


@throttle('review', 5, 24 * 3600, per_user=True)
def review_list(request):
    reviews = Review.objects.filter(is_approved=True).select_related('user')
    form = None
    if request.user.is_authenticated:
        form = ReviewForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, 'Thanks! Your review will appear once approved.')
            return redirect('reviews')
    return render(request, 'reviews/list.html', {'title': 'Reviews', 'reviews': reviews, 'form': form})
