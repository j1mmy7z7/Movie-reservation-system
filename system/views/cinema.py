import logging
from rest_framework import generics
from system.models import Cinema, Showtime
from system.serializers import CinemaSerializer, ShowtimeSerializer


logger = logging.getLogger(__name__)

class CinemaList(generics.ListAPIView):
    """
    List all cinemas.
    """
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer

    def get(self, request, *args, **kwargs):
        logger.info("CinemaList GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching cinema list: {e}")
            raise


class CinemaDetail(generics.RetrieveAPIView):
    """
    Retrieve a cinema by its ID.
    """
    serializer_class = CinemaSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            return Cinema.objects.prefetch_related("screens")

    def get(self, request, *args, **kwargs):
        logger.info("CinemaDetail GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching cinema detail: {e}")
            raise


class CinemaShowtimeList(generics.ListAPIView):
    """
    List all showtimes for a given cinema.
    """
    serializer_class = ShowtimeSerializer

    def get_queryset(self):
        return Showtime.objects.filter(screen__cinema_id=self.kwargs["cinema_id"])

    def get(self, request, *args, **kwargs):
        logger.info("CinemaShowtimeList GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching cinema showtime list: {e}")
            raise
