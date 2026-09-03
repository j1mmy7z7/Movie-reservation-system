import uuid
from django.conf import settings
from django.db import models
from .cinema import Seat
from .movies import Showtime


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)



class Ticket(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        HELD = "held", "Held"
        BOOKED = "booked", "Booked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="tickets")
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL, related_name="tickets")
    held_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    held_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("showtime", "seat")
