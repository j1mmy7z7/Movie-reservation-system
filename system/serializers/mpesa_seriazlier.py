import base64
import datetime
import requests
from django.conf import settings
from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from system.models import MpesaPayment, Ticket



def get_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]


def stk_push(*, phone_number, amount, account_reference, transaction_desc):
    token = get_access_token()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    response = requests.post(
        f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    response.raise_for_status()
    return response.json()   # contains CheckoutRequestID


class PaymentInitiateSerializer(serializers.Serializer):
    ticket_ids = serializers.ListField(child=serializers.UUIDField())
    phone_number = serializers.CharField()

    def create(self, validated_data):
        client = self.context["request"].user
        ticket_ids = validated_data["ticket_ids"]
        phone_number = validated_data["phone_number"]

        with transaction.atomic():
            tickets = Ticket.objects.select_for_update().filter(
                id__in=ticket_ids,
                status=Ticket.Status.HELD,
                held_by=client,
                held_until__gt=timezone.now(),
            )
            if tickets.count() != len(ticket_ids):
                raise serializers.ValidationError("One or more tickets are no longer held by you.")

            amount = sum(t.showtime.price for t in tickets)

            payment = MpesaPayment.objects.create(
                phone_number=phone_number,
                amount=amount,
                checkout_request_id="",   # filled in right after
            )
            tickets.update(payment=payment)

        response = stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=str(payment.id),
            transaction_desc="Movie ticket booking",
        )

        payment.checkout_request_id = response["CheckoutRequestID"]
        payment.save()

        return payment
