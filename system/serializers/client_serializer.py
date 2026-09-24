from rest_framework import serializers
from system.models import Client
from system.serializers import TicketSerializer


"""
Serializer for the Client model
used for serialize data for clients to view
"""
class ClientSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
           source="ticket_set",
           many=True,
           read_only=True,
       )

    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 'phone_number', 'tickets']


"""
Serializer for the Client model
used for registration of new clients
"""
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        client = Client(**validated_data)
        client.set_password(password)
        client.save()
        return client
