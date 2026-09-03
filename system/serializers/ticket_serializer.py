from rest_framework import serializers
from models import Ticket, Booking

# id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
# client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
# status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
# total_amount = models.DecimalField(max_digits=8, decimal_places=2)
# created_at = models.DateTimeField(auto_now_add=True)


class TicketSerializer(serializers.Serializer):
    class Meta:
        model = Ticket
        fields = ['id', 'showtime', 'seat', 'booking', 'held_by', 'held_until']


class BookingSerializer(serializers.Serializer):
    class Meta:
        model = Booking
        fields = ['id', 'client', 'status', 'total_amount', 'created_at']
