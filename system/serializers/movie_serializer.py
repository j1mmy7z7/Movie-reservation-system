from rest_framework import serializers
from system.models import Movie, Showtime


class MovieSerializer(serializers.Serializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration_minutes', 'release_date']


class ShowtimeSerializer(serializers.Serializer):
    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'screen', 'start_time', 'end_time', 'price']
