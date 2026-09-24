import logging

from rest_framework import generics, response, views, status
from system.models import (Ticket, MpesaPayment)
from system.serializers import (
    TicketSerializer,
    HoldSerializer,
    PaymentInitiateSerializer,
    MpesaPaymentSerializer,
)
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


logger = logging.getLogger(__name__)

class ShowtimeTicketList(generics.ListAPIView):
    """
    List all tickets for a given showtime.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(showtime_id=self.kwargs["showtime_id"])

    def get(self, request, *args, **kwargs):
        logger.info("ShowtimeTicketList GET request received")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching showtime ticket list: {e}")
            raise


# class BookingList(generics.ListCreateAPIView):
#     """
#     List and create bookings for the authenticated client.
#     """
#     serializer_class = BookingSerializer

#     def get_queryset(self):
#         return Booking.objects.filter(client=self.request.user)



class HoldTickets(generics.CreateAPIView):
    """
    Hold tickets for the authenticated client.
    """
    serializer_class = HoldSerializer
    permission_classes = [IsAuthenticated]


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["showtime_id"] = self.kwargs["showtime_id"]
        return context

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"HoldTickets POST request received for user {request.user.username}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            tickets = serializer.save()
            logger.info(f"HoldTickets POST request: held {len(tickets)} tickets")
            return response.Response(data=TicketSerializer(tickets, many=True).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error holding tickets for user {request.user.username}: {e}")
            raise


class InitiatePayment(generics.CreateAPIView):
    """
    Initiate a payment via M-Pesa for the booked tickets.
    """
    serializer_class = PaymentInitiateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"InitiatePayment POST request received for user {request.user.username}")
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            payment = serializer.save()
            logger.info(f"Payment initiated successfully for user {request.user.username}")
            return response.Response({
                "payment_id": payment.id,
                "status": payment.status,
                "message": "Check your phone to complete payment.",
            })
        except Exception as e:
            logger.error(f"Error initiating payment for user {request.user.username}: {e}")
            raise

class CancelTickets(views.APIView):
    """
    Cancel a booking by marking tickets as available.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"CancelTickets POST request received for user {request.user.username}")
            ticket_ids = request.data.get("ticket_ids", [])
            tickets = Ticket.objects.filter(
                id__in=ticket_ids,
                held_by=request.user,
            ).filter(
                Q(status=Ticket.Status.HELD) |
                Q(status=Ticket.Status.BOOKED)
            )
            cutoff = timezone.now() + timedelta(minutes=10)
            tickets = tickets.filter(showtime__start_time__gt=cutoff)

            count = tickets.update(
                status=Ticket.Status.AVAILABLE, held_by=None, held_until=None, payment=None
            )
            logger.info(f"CancelTickets POST request: cancelled {count} tickets")
            return response.Response({"cancelled": count})
        except Exception as e:
            logger.error(f"Error cancelling tickets for user {request.user.username}: {e}")
            raise


class MpesaCallback(views.APIView):
    """
    Handle the M-Pesa callback from the payment gateway.
    """


    def post(self, request):
        body = request.data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = body.get("CheckoutRequestID")
        result_code = body.get("ResultCode")

        try:
            payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
            logger.info(f"MpesaCallback POST request: payment {payment.pk} updated")
        except MpesaPayment.DoesNotExist:
            logger.warning(f"MpesaCallback POST request: payment with checkout_request_id {checkout_request_id} not found")
            return response.Response({"ResultCode": 0, "ResultDesc": "Accepted"})

        if result_code == 0:
            metadata = {
                item["Name"]: item.get("Value")
                for item in body.get("CallbackMetadata", {}).get("Item", [])
            }
            payment.status = MpesaPayment.Status.COMPLETED
            payment.mpesa_transaction_id = metadata.get("MpesaReceiptNumber", "")
            payment.save()
            payment.tickets.update(status=Ticket.Status.BOOKED)
            logger.info(f"MpesaCallback POST request: payment {payment.pk} updated")
        else:
            payment.status = MpesaPayment.Status.FAILED
            payment.save()
            logger.info(f"MpesaCallback POST request: payment {payment.pk} failed")

        return response.Response({"ResultCode": 0, "ResultDesc": "Accepted"})

class PaymentStatus(generics.RetrieveAPIView):
    """
    Check if the payment has been completed or failed.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MpesaPaymentSerializer
    lookup_field = "id"

    def get_queryset(self):
        return MpesaPayment.objects.filter(tickets__held_by=self.request.user).distinct()

    def get(self, request, *args, **kwargs):
        logger.info(f"PaymentStatus GET request received for user {self.request.user.username}")
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error fetching payment status for user {self.request.user.username}: {e}")
            raise
