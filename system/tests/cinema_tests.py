from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from system.models import Cinema, Seat, Screen, Movie, Showtime


class CinemaTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.cinema = Cinema.objects.create(name="Test Cinema", address="Test Location")
        self.screen = Screen.objects.create(cinema=self.cinema, name="Test Screen")
        self.movie = Movie.objects.create(title="Test Movie", duration_minutes=120, description="Test Description movie 1", release_date=timezone.now())
        self.movie2 = Movie.objects.create(title="Test Movie 2", duration_minutes=120, description="Test Description movie 2", release_date=timezone.now())
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=3),
            price=0.00,
        )

    def test_cinema_list(self):
        response = self.client.get('/cinemas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Cinema")

    def test_screen_list(self):
        response = self.client.get(f'/cinemas/{self.cinema.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['screens']), 1)
        self.assertEqual(response.data['screens'][0]['name'], "Test Screen")

    def test_movie_list(self):
        response = self.client.get('/movies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], "Test Movie")
        self.assertEqual(response.data[1]['title'], "Test Movie 2")

    def test_movie_detail(self):
        response = self.client.get(f'/movies/{self.movie.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Movie")
        self.assertEqual(response.data['duration_minutes'], 120)
        self.assertEqual(response.data['description'], "Test Description movie 1")
