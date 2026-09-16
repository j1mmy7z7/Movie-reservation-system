import logging

from rest_framework import generics
from system.serializers import RegistrationSerializer, ClientSerializer
from rest_framework.permissions import IsAuthenticated


logger = logging.getLogger(__name__)

class Register(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"Registering client: {request.data.get('username')}")
        try:
            response = super().post(request, *args, **kwargs)
            logger.info(f"Client registered successfully: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            raise


class ClientDetail(generics.RetrieveAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        logger.info(f"Fetching data for client: {self.request.user.username}")
        try:
            return self.request.user
        except Exception as e:
            logger.error(f"Error fetching client data: {e}")
            raise
