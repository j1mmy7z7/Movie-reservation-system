from rest_framework import generics
from system.models import Booking, Seat, Ticket
from system.serializers import BookingSerializer, SeatSerializer, TicketSerializer


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
