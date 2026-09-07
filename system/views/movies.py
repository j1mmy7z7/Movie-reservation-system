from rest_framework import generics
from system.serializers import MovieSerializer
from system.models import Movie, Showtime
from django.db.models import Count, Prefetch
from django.db.models import Q

class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MovieSerializer
    def get_queryset(self):
        if self.request.method == "GET":
            return Movie.objects.prefetch_related(
                Prefetch(
                    "showtimes",
                    queryset=Showtime.objects.annotate(
                        available_seats_count=Count("tickets", filter=Q(tickets__status="available"))
                    ),
                )
            )
        return Movie.objects.all()
