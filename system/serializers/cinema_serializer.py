from rest_framework import serializers
from system.models import Cinema, Screen, Seat


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'cinema', 'name']


class CinemaSerializer(serializers.ModelSerializer):
    screens = ScreenSerializer(many=True, read_only=True)

    class Meta:
        model = Cinema
        fields = ['id', 'name', 'address', 'screens']


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'screen', 'row_label', 'seat_number']
