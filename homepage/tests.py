from django.test import Client, TestCase
from django.urls import reverse

class HomepageTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_homepage_ok(self):
        url = reverse('homepage')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
