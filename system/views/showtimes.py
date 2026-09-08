from rest_framework import generics
from system.models import Showtime
from system.serializers import ShowtimeSerializer

class ShowtimeList(generics.ListAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer

class ShowtimeDetail(generics.RetrieveAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer
