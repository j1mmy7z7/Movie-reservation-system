
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from rest_framework import serializers
from django.db import transaction
from system.models import (
    Ticket,
    MpesaPayment,
)


"""
this is how long one can book tickets before initiatiing payments
if the time is past but payment has been initiated, the hold duration is extended
since tickets with payments are filtered out, the hold duration is extended to cover the booking cutoff
"""
HOLD_DURATION = timedelta(minutes=10)

""" people can book ticks till 10 minutes before the showtime """
BOOKING_CUTOFF = timedelta(minutes=10)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'showtime', 'seat', 'booking', 'held_by', 'held_until']


# class BookingSerializer(serializers.ModelSerializer):
#     """
#     This serializer is meant for creating a booking for the tickets.
#     """
#     ticket_ids = serializers.ListField(
#         child=serializers.UUIDField(), write_only=True
#     )

#     class Meta:
#             model = Booking
#             fields = ["id", "status", "total_amount", "created_at", "ticket_ids"]
#             read_only_fields = ["id", "status", "total_amount", "created_at"]

#     @transaction.atomic
#     def create(self, validated_data):
#         client = self.context['request'].user
#         ticket_ids = validated_data.pop('ticket_ids')
#         tickets = Ticket.objects.select_for_update().filter(
#             id__in=ticket_ids,
#             status=Ticket.Status.HELD,
#             held_by=client,
#             held_until__gt=timezone.now(),
#         )
#         if tickets.count() != len(ticket_ids):
#             raise serializers.ValidationError("Some tickets are not held by the client or have expired.")

#         total = sum(t.showtime.price for t in tickets)
#         booking = Booking.objects.create(client=client, total_amount=total)
#         tickets.update(booking=booking)
#         return booking


class HoldSerializer(serializers.Serializer):
    """
    This serializer is meant for holding tickets for a client.
    It validates the seat_ids and holds the tickets.

    """

    seat_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    def create(self, validated_data):
        client = self.context["request"].user
        showtime_id = self.context["showtime_id"]
        seat_ids = validated_data["seat_ids"]

        with transaction.atomic():
            base = Ticket.objects.select_for_update().filter(
                showtime_id=showtime_id,
                seat_id__in=seat_ids,
            )

            found_seat_ids = set(base.values_list("seat_id", flat=True))
            missing = set(seat_ids) - found_seat_ids
            if missing:
                raise serializers.ValidationError({
                    "detail": "One or more seats don't exist for this showtime.",
                    "seat_ids": list(missing),
                })

            if base.filter(showtime__start_time__lte=timezone.now() + BOOKING_CUTOFF).exists():
                raise serializers.ValidationError("This showtime is starting too soon to book.")

            claimable = base.filter(
                Q(status=Ticket.Status.AVAILABLE) |
                Q(status=Ticket.Status.HELD, held_until__lt=timezone.now())
            )
            claimable_seat_ids = set(claimable.values_list("seat_id", flat=True))
            taken = set(seat_ids) - claimable_seat_ids
            if taken:
                raise serializers.ValidationError({
                    "detail": "One or more selected seats are already taken.",
                    "seat_ids": list(taken),
                })

            locked_ok = claimable.filter(
                Q(payment__isnull=True) | Q(payment__status=MpesaPayment.Status.FAILED)
            )
            locked_ok_seat_ids = set(locked_ok.values_list("seat_id", flat=True))
            payment_locked = set(seat_ids) - locked_ok_seat_ids
            if payment_locked:
                raise serializers.ValidationError({
                    "detail": "One or more seats have a payment in progress.",
                    "seat_ids": list(payment_locked),
                })

            locked_ok.update(
                status=Ticket.Status.HELD,
                held_by=client,
                held_until=timezone.now() + HOLD_DURATION,
            )

        return Ticket.objects.filter(showtime_id=showtime_id, seat_id__in=seat_ids)
