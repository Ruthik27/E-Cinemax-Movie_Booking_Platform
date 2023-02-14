from django.db import models

# Create your models here.

from datetime import datetime, timedelta
from cinema_ebooking_system import constants
from core.models import TimeStamp


class Movie(TimeStamp):
   title = models.CharField(max_length=255)
   alias = models.CharField(max_length=255, blank=True, null=True)
   movie_code = models.CharField(max_length=255, blank=True, null=True)
   expire_date = models.DateTimeField(null=True, blank=True)
   category = models.CharField(max_length=100, choices=constants.CATEGORY, default="drama")
   cast = models.TextField(null=True, blank=True)
   director = models.CharField(max_length=255, null=True, blank=True)
   producer = models.CharField(max_length=255, null=True, blank=True)
   poster_image = models.FileField(upload_to="static/images/", null=True)
   trailer = models.TextField(default="Trailer not available")
   rating = models.CharField(max_length=10, default="G")
   synopsis = models.TextField(default="Just a movie")
   is_playing = models.BooleanField(default=False)
   
   def __str__(self):
        return self.title


class Show(TimeStamp):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    show_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        timings = str(self.start_time) +" - "+ str(self.end_time)
        return timings


class Promotion(TimeStamp):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    promo_code = models.CharField(max_length=100, default='promo1', unique=True)
    off_amount = models.FloatField(default=0)
    off_percent = models.FloatField(default=0)
    promo_type = models.CharField(max_length=100, choices=constants.COUPON_TYPES, default="percent")
    min_amount = models.FloatField(default=0)
    expiration_date = models.DateField(blank=True, null=True)
    is_sent = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.promo_code


class Seat(TimeStamp):
    row = models.CharField(max_length=10, default='A')
    number = models.IntegerField(default=1)
    room = models.CharField(max_length=10, default='A')
    show = models.ForeignKey(Show, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.row





    



   

