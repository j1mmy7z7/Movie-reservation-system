import logging
from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


@extend_schema(
    tags=["System"],
    auth=[],
    responses=inline_serializer(
        name="HealthCheckResponse",
        fields={
            "status": serializers.ChoiceField(choices=["healthy", "unhealthy"]),
            "checks": serializers.DictField(child=serializers.CharField()),
        },
    ),
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint to verify the status of the system.
    """
    health_status = {
        'status': 'healthy',
        'checks': {},
    }

    try:
        db_conn = connections['default']
        db_conn.cursor()
        health_status['checks']['database'] = 'healthy'
    except OperationalError as e:
        logger.error(f"Database error: {e}")
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = 'error'

    if health_status['status'] == 'unhealthy':
        logger.error("Health check failed")
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response(health_status)
