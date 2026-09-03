import uuid
from django.db import models
from django.core.exceptions import ValidationError
from .cinema import Screen


class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    release_date = models.DateField()

class Showtime(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name="showtimes")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)   # flat price, no seat tiers

    def clean(self):
        overlapping = Showtime.objects.filter(
            screen=self.screen,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("This screen already has a showtime in that time range.")
