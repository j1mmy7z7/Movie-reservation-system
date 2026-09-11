from rest_framework import generics, response
from system.models import Booking, Ticket
from system.serializers import (
    BookingSerializer,
    TicketSerializer,
    HoldSerializer,
)


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
