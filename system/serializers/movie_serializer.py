from rest_framework import serializers
from system.models import Movie, Showtime
from .cinema_serializer import ScreenSerializer

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration_minutes', 'release_date']


class ShowtimeSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    screen = ScreenSerializer(read_only=True)
    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'screen', 'start_time', 'end_time', 'price']
