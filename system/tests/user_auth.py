from rest_framework.test import APIClient
from django.test import TestCase
from system.models import Client

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Client.objects.create_user(username='testuser', password='testpassword')

    def test_user_registration(self):
        self.assertIsNotNone(self.user)
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_user_login(self):
        response = self.client.post('/auth/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)

    def test_random_user(self):
        response = self.client.post('/auth/login/', {'username': 'randomuser', 'password': 'randompassword'})
        self.assertEqual(response.status_code, 401)
