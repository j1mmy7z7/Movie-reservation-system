from rest_framework import generics, response, views
from system.models import Booking, Ticket
from system.serializers import (
    BookingSerializer,
    TicketSerializer,
    HoldSerializer,
    PaymentInitiateSerializer,
)
from django.utils import timezone
from datetime import timedelta


class ShowtimeTicketList(generics.ListAPIView):
    """
    List all tickets for a given showtime.
    """

    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(showtime_id=self.kwargs["showtime_id"])


class BookingList(generics.ListCreateAPIView):
    """
    List and create bookings for the authenticated client.
    """
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)



class HoldTickets(generics.CreateAPIView):
    serializer_class = HoldSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["showtime_id"] = self.kwargs["showtime_id"]
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = serializer.save()
        return response.Response(data=TicketSerializer(tickets, many=True).data)



class InitiatePayment(generics.CreateAPIView):
    serializer_class = PaymentInitiateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return response.Response({
            "payment_id": payment.id,
            "status": payment.status,
            "message": "Check your phone to complete payment.",
        })

class CancelBooking(views.APIView):
    """
    Cancel a booking by marking tickets as available.
    """

    def post(self, request):
        ticket_ids = request.data.get("ticket_ids", [])
        tickets = Ticket.objects.filter(
            id__in=ticket_ids, status=Ticket.Status.BOOKED, held_by=request.user
        )
        cutoff = timezone.now() + timedelta(minutes=10)
        tickets = tickets.filter(showtime__start_time__gt=cutoff)

        count = tickets.update(
            status=Ticket.Status.AVAILABLE, held_by=None, held_until=None, payment=None
        )
        return response.Response({"cancelled": count})
