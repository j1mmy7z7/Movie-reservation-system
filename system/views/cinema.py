from rest_framework import generics
from system.models import Cinema, Showtime
from system.serializers import CinemaSerializer, ShowtimeSerializer


class CinemaList(generics.ListAPIView):
    """
    List all cinemas.
    """
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer

class CinemaDetail(generics.RetrieveAPIView):
    """
    Retrieve a cinema by its ID.
    """
    serializer_class = CinemaSerializer
    def get_queryset(self):
            if self.request.method == "GET":
                return Cinema.objects.prefetch_related("screens")
            return Cinema.objects.all()

class CinemaShowtimeList(generics.ListAPIView):
    """
    List all showtimes for a given cinema.
    """
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        return Showtime.objects.filter(screen__cinema_id=self.kwargs["cinema_id"])
