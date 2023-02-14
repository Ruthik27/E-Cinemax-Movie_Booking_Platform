from django.shortcuts import render
from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import encoding
from django.views.generic import View, TemplateView, CreateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Booking, Seat, Ticket
# Create your views here.


class BookingListView(TemplateView):
    template_name='core/ticket_booking.html'


class BookingHistoryListView(LoginRequiredMixin,TemplateView):
    template_name = 'ticket_booking_history.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        bookings = Booking.objects.filter(user=request.user)
        tickets =  Ticket.objects.filter(booking__in=bookings)

        return render(
            request, 
            "core/ticket_booking_history.html",
            context={
                    'bookings':bookings, 
                    "tickets":tickets,
                    }
            ) 



