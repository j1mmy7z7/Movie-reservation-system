from rest_framework import generics
from system.models import Cinema
from system.serializers import CinemaSerializer


class CinemaList(generics.ListAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer

class CinemaDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CinemaSerializer
    def get_queryset(self):
            if self.request.method == "GET":
                return Cinema.objects.prefetch_related("screens")
            return Cinema.objects.all()
