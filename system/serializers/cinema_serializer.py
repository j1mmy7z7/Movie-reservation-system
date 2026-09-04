from rest_framework import serializers
from system.models import Cinema, Screen, Seat


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ['id', 'name', 'address']


class ScreenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screen
        fields = ['id', 'cinema', 'name']


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'screen', 'row_label', 'seat_number']
