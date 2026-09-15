
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from rest_framework import serializers
from django.db import transaction
from system.models import Ticket, Booking, MpesaPayment

HOLD_DURATION = timedelta(minutes=10)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'showtime', 'seat', 'booking', 'held_by', 'held_until']


class BookingSerializer(serializers.ModelSerializer):
    """
    This serializer is meant for creating a booking for the tickets.
    """
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
        tickets = Ticket.objects.select_for_update().filter(
            id__in=ticket_ids,
            status=Ticket.Status.HELD,
            held_by=client,
            held_until__gt=timezone.now(),
        )
        if tickets.count() != len(ticket_ids):
            raise serializers.ValidationError("Some tickets are not held by the client or have expired.")

        total = sum(t.showtime.price for t in tickets)
        booking = Booking.objects.create(client=client, total_amount=total)
        tickets.update(booking=booking)
        return booking


class HoldSerializer(serializers.Serializer):
    """
    This serializer is meant for holding tickets for a client.
    It validates the seat_ids and holds the tickets.

    """

    seat_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    @transaction.atomic
    def create(self, validated_data):
        client = self.context['request'].user
        showtime_id = self.context['showtime_id']
        seat_ids = validated_data['seat_ids']

        tickets = Ticket.objects.select_for_update().filter(
            showtime_id=showtime_id,
            seat_id__in=seat_ids,
        ).filter(
            Q(status=Ticket.Status.AVAILABLE) | Q(status=Ticket.Status.HELD, held_until__lt=timezone.now())
        ).filter(
            Q(payment__isnull=True) | Q(payment__status=MpesaPayment.Status.FAILED)
        )

        if tickets.count() != len(seat_ids):
                        raise serializers.ValidationError("One or more seats are no longer available.")

        tickets.update(
            status=Ticket.Status.HELD,
            held_by=client,
            held_until=timezone.now() + HOLD_DURATION,
        )

        return Ticket.objects.filter(showtime=showtime, seat_id__in=seat_ids)
