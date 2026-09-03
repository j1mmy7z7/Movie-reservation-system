import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class Client(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, blank=True)
