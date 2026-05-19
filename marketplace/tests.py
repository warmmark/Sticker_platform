from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Favorite, Listing, Profile


class MarketplaceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='artist', password='pass12345')
        self.buyer = User.objects.create_user(username='buyer', password='pass12345')
        self.listing = Listing.objects.create(seller=self.user, title='Стикеры', category=Listing.Category.STICKERS, description='Описание', price=1000, deadline_days=3)

    def test_profile_created_automatically(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_catalog_available(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Стикеры')

    def test_favorite_requires_login_then_adds(self):
        self.client.login(username='buyer', password='pass12345')
        response = self.client.get(reverse('toggle_favorite', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.buyer, listing=self.listing).exists())

    def test_create_order(self):
        self.client.login(username='buyer', password='pass12345')
        response = self.client.post(reverse('create_order', args=[self.listing.pk]), {'comment': 'Нужен заказ'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.buyer.buyer_orders.count(), 1)
