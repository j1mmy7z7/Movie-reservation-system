from django.db import models
import uuid


class Cinema(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)


class Screen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="screens")
    name = models.CharField(max_length=50)   #

    class Meta:
        unique_together = ("cinema", "name")


class Seat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name="seats")
    row_label = models.CharField(max_length=2)
    seat_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("screen", "row_label", "seat_number")
