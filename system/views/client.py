from rest_framework import generics
from system.serializers import RegistrationSerializer, ClientSerializer
# from system.models import Client
from rest_framework.permissions import IsAuthenticated


class Register(generics.CreateAPIView):
    serializer_class = RegistrationSerializer


class ClientDetail(generics.RetrieveAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
