from rest_framework import generics, response, views
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



class ShowtimeTicketList(generics.ListAPIView):
    """
    List all tickets for a given showtime.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(showtime_id=self.kwargs["showtime_id"])


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = serializer.save()
        return response.Response(data=TicketSerializer(tickets, many=True).data)



class InitiatePayment(generics.CreateAPIView):
    """
    Initiate a payment via M-Pesa for the booked tickets.
    """
    serializer_class = PaymentInitiateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return response.Response({
            "payment_id": payment.id,
            "status": payment.status,
            "message": "Check your phone to complete payment.",
        })

class CancelBooking(views.APIView):
    """
    Cancel a booking by marking tickets as available.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket_ids = request.data.get("ticket_ids", [])
        tickets = Ticket.objects.filter(
            id__in=ticket_ids, status=Ticket.Status.BOOKED, held_by=request.user
        )
        cutoff = timezone.now() + timedelta(minutes=10)
        tickets = tickets.filter(showtime__start_time__gt=cutoff)

        count = tickets.update(
            status=Ticket.Status.AVAILABLE, held_by=None, held_until=None, payment=None
        )
        return response.Response({"cancelled": count})


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
        except MpesaPayment.DoesNotExist:
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
        else:
            payment.status = MpesaPayment.Status.FAILED
            payment.save()

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
