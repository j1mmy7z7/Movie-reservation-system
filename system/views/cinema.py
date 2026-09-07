from rest_framework import generics
from system.models import Cinema, Showtime
from system.serializers import CinemaSerializer, ShowtimeSerializer


class CinemaList(generics.ListAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer

class CinemaDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CinemaSerializer
    def get_queryset(self):
            if self.request.method == "GET":
                return Cinema.objects.prefetch_related("screens")
            return Cinema.objects.all()

class CinemaShowtimeList(generics.ListAPIView):
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        return Showtime.objects.filter(screen__cinema_id=self.kwargs["cinema_id"])
