from rest_framework import generics
from system.models import Showtime
from system.serializers import ShowtimeSerializer

class ShowtimeList(generics.ListCreateAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer

class ShowtimeDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShowtimeSerializer
    def get_queryset(self):
            if self.request.method == "GET":
                return Cinema.objects.prefetch_related("screens")
            return Cinema.objects.all()
