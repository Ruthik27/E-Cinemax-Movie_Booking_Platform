from django.db import models
from django.db.models.fields import TextField
from cinema_ebooking_system import constants
from core.models import TimeStamp, User

# Create your models here.


class CreditCard(TimeStamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.TextField(null=True, blank=True)
    name_on_card = models.CharField(max_length=25, null=True, blank=True)
    type = models.CharField(max_length=20, choices=constants.CARD_TYPES)
    expiration_date = models.CharField(max_length=25, null=True, blank=True)
    billing_address = models.CharField(max_length=100, null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)
    public_key = models.TextField(null=True, blank=True)

    
