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
