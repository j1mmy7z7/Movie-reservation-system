from rest_framework import serializers
from system.models import Movie, Showtime


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'duration_minutes', 'release_date']


class ShowtimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Showtime
        fields = ['id', 'movie', 'screen', 'start_time', 'end_time', 'price']
