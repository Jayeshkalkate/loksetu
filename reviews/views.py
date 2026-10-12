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
    my_reviews = Review.objects.filter(user=request.user) if request.user.is_authenticated else Review.objects.none()
    return render(request, 'reviews/list.html', {'title': 'Reviews', 'reviews': reviews, 'form': form, 'my_reviews': my_reviews})


@login_required
def review_edit(request, pk):
    from django.shortcuts import get_object_or_404
    review = get_object_or_404(Review, pk=pk, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.is_approved = False  # edited content must be reviewed before publication again
        review.save()
        messages.success(request, 'Your review was updated and sent for approval again.')
        return redirect('reviews')
    return render(request, 'reviews/edit.html', {'form': form, 'review': review})


@login_required
def review_delete(request, pk):
    from django.shortcuts import get_object_or_404
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Your review was deleted.')
        return redirect('reviews')
    return render(request, 'reviews/delete.html', {'review': review})
