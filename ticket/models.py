from django.db import models
from cinema_ebooking_system import constants
from core.models import TimeStamp, User
from movie.models import Promotion, Seat, Show
# Create your models here.

class Booking(TimeStamp):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat_rows = models.TextField(blank=True, null=True)
    no_of_ticket = models.IntegerField(default=1)
    booking_total = models.FloatField(default=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_refunded = models.BooleanField(default=False)
    is_refundable = models.BooleanField(default=True)  

class Ticket(TimeStamp):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, null=True, blank=True)
    show = models.ForeignKey(Show, on_delete=models.CASCADE, null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_refundable = models.BooleanField(default=True)
    category = models.CharField(max_length=20, choices=constants.TICKET_TYPES, default='adult')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)

  