from django.template import response
from django.template.base import re
from rest_framework.test import APIClient, APITestCase
from system.models import (
    Screen,
    Showtime,
    Ticket,
    Cinema,
    Movie,
    Client,
    Seat,
)
from datetime import timedelta
from django.utils import timezone


class Test_Booking(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.cinema = Cinema.objects.create(name="Test Cinema", address="Test Location")
        self.screen = Screen.objects.create(cinema=self.cinema, name="Test Screen")
        self.movie = Movie.objects.create(title="Test Movie", duration_minutes=120, description="Test Description movie 1", release_date=timezone.now())
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=3),
            price=0.00,
        )
        self.seat = Seat.objects.create(screen=self.screen, row_label="A", seat_number=1)
        self.client_1 = Client.objects.create_user(username="client1", password="testpassword1")
        self.client_2 = Client.objects.create_user(username="client2", password="testpassword2")
        self.ticket = Ticket.objects.create(
            showtime=self.showtime,
            seat=self.seat,
            status=Ticket.Status.AVAILABLE,
        )
    def test_list_tickets(self):
        response = self.client.post('/auth/login/', {'username': self.client_1.username, 'password': 'testpassword1'})
        self.assertEqual(response.status_code, 200)
        token_1 = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_1}"
        )
        response = self.client.get(f'/showtimes/{self.showtime.id}/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_booking(self):
        response = self.client.post('/auth/login/', {'username': self.client_1.username, 'password': 'testpassword1'})
        self.assertEqual(response.status_code, 200)
        token_1 = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_1}"
        )
        response = self.client.post(f'/showtimes/{self.showtime.id}/hold/', {'seat_ids': [str(self.seat.id)]})
        self.assertEqual(response.status_code, 201)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.HELD)
        self.assertEqual(self.ticket.seat, self.seat)
        self.assertEqual(self.ticket.held_by, self.client_1)

        """
        cancel booking
        """
        response = self.client.post('/tickets/cancel/', {'ticket_ids': [str(self.ticket.id)]}, format='json')
        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, Ticket.Status.AVAILABLE)



class Booking_cases(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.cinema = Cinema.objects.create(name="Test Cinema", address="Test Location")
        self.screen = Screen.objects.create(cinema=self.cinema, name="Test Screen")
        self.movie = Movie.objects.create(title="Test Movie", duration_minutes=120, description="Test Description movie 1", release_date=timezone.now())
        """
        this is for testing booking when showtime is started
        """
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=3),
            price=0.00,
        )
        self.showtime_2 = Showtime.objects.create(
            movie=self.movie,
            screen=self.screen,
            start_time=timezone.now() + timedelta(hours=3),
            end_time=timezone.now() + timedelta(hours=6),
            price=0.00,
        )

        self.seat = Seat.objects.create(screen=self.screen, row_label="A", seat_number=1)
        self.client_1 = Client.objects.create_user(username="client1", password="testpassword1")
        self.client_2 = Client.objects.create_user(username="client2", password="testpassword2")
        self.ticket = Ticket.objects.create(
            showtime=self.showtime,
            seat=self.seat,
            status=Ticket.Status.AVAILABLE,
        )
        self.ticket_2 = Ticket.objects.create(
            showtime=self.showtime_2,
            seat=self.seat,
            status=Ticket.Status.AVAILABLE,
        )

    def test_book_started_showtime(self):
        response = self.client.post('/auth/login/', {'username': self.client_1.username, 'password': 'testpassword1'})
        self.assertEqual(response.status_code, 200)
        token_1 = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_1}"
        )
        response = self.client.post(f'/showtimes/{self.showtime.id}/hold/', {'seat_ids': [str(self.seat.id)]})
        self.assertEqual(response.status_code, 400)

    def test_already_held_ticket(self):
        response = self.client.post('/auth/login/', {'username': self.client_1.username, 'password': 'testpassword1'})
        self.assertEqual(response.status_code, 200)
        token_1 = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_1}"
        )
        response = self.client.post(f'/showtimes/{self.showtime_2.id}/hold/', {'seat_ids': [str(self.seat.id)]})
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/auth/login/', {'username': self.client_2.username, 'password': 'testpassword2'})
        self.assertEqual(response.status_code, 200)
        token_2 = response.data['access']
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token_2}"
        )
        response = self.client.post(f'/showtimes/{self.showtime_2.id}/hold/', {'seat_ids': [str(self.seat.id)]})
        self.assertEqual(response.status_code, 400)
