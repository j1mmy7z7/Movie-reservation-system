from rest_framework import generics
from system.models import Showtime
from system.serializers import ShowtimeSerializer

class ShowtimeList(generics.ListCreateAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer

class ShowtimeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
