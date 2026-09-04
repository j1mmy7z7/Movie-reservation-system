from rest_framework import serializers
from system.models import Ticket, Booking


class TicketSerializer(serializers.Serializer):
    class Meta:
        model = Ticket
        fields = ['id', 'showtime', 'seat', 'booking', 'held_by', 'held_until']


class BookingSerializer(serializers.Serializer):
    class Meta:
        model = Booking
        fields = ['id', 'client', 'status', 'total_amount', 'created_at']
