from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import Review

User = get_user_model()
PW = 'Str0ng-pass-phrase-77'


class ReviewCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('reviewuser', 'review@example.com', PW)
        cls.other = User.objects.create_user('reviewother', 'reviewother@example.com', PW)

    def setUp(self):
        cache.clear()

    def test_user_can_edit_own_review_and_it_returns_to_moderation(self):
        review = Review.objects.create(user=self.user, rating=4, comment='A useful and helpful service.', is_approved=True)
        self.client.force_login(self.user)
        response = self.client.post(reverse('review_edit', args=[review.pk]), {
            'rating': 5, 'comment': 'The service is very useful and helpful.'})
        self.assertRedirects(response, reverse('reviews'))
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertFalse(review.is_approved)

    def test_user_can_delete_own_review_with_post(self):
        review = Review.objects.create(user=self.user, rating=4, comment='A useful and helpful service.')
        self.client.force_login(self.user)
        response = self.client.post(reverse('review_delete', args=[review.pk]))
        self.assertRedirects(response, reverse('reviews'))
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_cannot_edit_or_delete_another_users_review(self):
        review = Review.objects.create(user=self.other, rating=4, comment='A useful and helpful service.')
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('review_edit', args=[review.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse('review_delete', args=[review.pk])).status_code, 404)
