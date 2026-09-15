from rest_framework import serializers
from system.models import Client


"""
Serializer for the Client model
used for serialize data for clients to view
"""
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'username', 'email', 'phone_number']


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
