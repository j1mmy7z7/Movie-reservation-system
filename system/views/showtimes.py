import logging
from rest_framework import generics
from system.models import Showtime
from system.serializers import ShowtimeSerializer

logger = logging.getLogger(__name__)

class ShowtimeList(generics.ListAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer

    def get(self, request, *args, **kwargs):
        logger.info("ShowtimeList GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching showtimes: {e}")
            raise


class ShowtimeDetail(generics.RetrieveAPIView):
    queryset = Showtime.objects.all()
    serializer_class = ShowtimeSerializer

    def get(self, request, *args, **kwargs):
        logger.info("ShowtimeDetail GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching showtime detail: {e}")
            raise
