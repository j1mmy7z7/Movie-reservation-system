import logging
from rest_framework import generics
from system.serializers import MovieSerializer
from system.models import Movie, Showtime
from django.db.models import Count, Prefetch
from django.db.models import Q

logger = logging.getLogger(__name__)

class MovieList(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    def get(self, request, *args, **kwargs):
        logger.info("MovieList GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching movies: {e}")
            raise

class MovieDetail(generics.RetrieveAPIView):
    serializer_class = MovieSerializer
    def get_queryset(self):
        return Movie.objects.prefetch_related(
            Prefetch(
                    "showtimes",
                    queryset=Showtime.objects.annotate(
                        available_seats_count=Count("tickets", filter=Q(tickets__status="available"))
                    ),
                )
            )

    def get(self, request, *args, **kwargs):
        logger.info("MovieDetail GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching movie detail: {e}")
            raise
