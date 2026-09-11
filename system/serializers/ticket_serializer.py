
from django.utils import timezone

from rest_framework import serializers
from django.db import transaction
from system.models import Ticket, Booking


class TicketSerializer(serializers.Serializer):
    class Meta:
        model = Ticket
        fields = ['id', 'showtime', 'seat', 'booking', 'held_by', 'held_until']


class BookingSerializer(serializers.ModelSerializer):
    ticket_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    class Meta:
            model = Booking
            fields = ["id", "status", "total_amount", "created_at", "ticket_ids"]
            read_only_fields = ["id", "status", "total_amount", "created_at"]

    @transaction.atomic
    def create(self, validated_data):
        client = self.context['request'].user
        ticket_ids = validated_data.pop('ticket_ids')
        tickets = Ticket.objects.select_for_update().filter(id__in=ticket_ids, status=Ticket.Status.HELD,
            held_by=client, held_until__gt=timezone.now())
        if tickets.count() != len(ticket_ids):
            raise serializers.ValidationError("Some tickets are not held by the client or have expired.")

        total = sum(t.showtime.price for t in tickets)
        booking = Booking.objects.create(client=client, total_amount=total)
        tickets.update(booking=booking)
        return booking
