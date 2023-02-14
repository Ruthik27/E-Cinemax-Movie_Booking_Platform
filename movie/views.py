import stripe
import braintree
import os

from typing import final
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView, CreateView
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Movie, Promotion, Seat, Show
from core.models import User
from ticket.models import Ticket, Booking
from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Sum
from django.http import JsonResponse
from card.models import CreditCard
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY

def asymetric_decrypt_string(stringToDecrypt, privateKeyAsString):
    """
    Decrypts a string with a private key as string
    """
    # convert private key from string to bytes
    keyAsBytes = bytes(privateKeyAsString, "utf-8")
    private_key = serialization.load_pem_private_key(
        keyAsBytes, password=None, backend=default_backend()
    )

    # CONVERSION of BASE64 representation string to raw bytes
    textToDecryptAsBytes = base64.urlsafe_b64decode(stringToDecrypt)

    # Decrypt
    decryptedBytes = private_key.decrypt(
        textToDecryptAsBytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    decryptedString = decryptedBytes.decode("utf-8")

    return decryptedString

class MovieDetailView(View):

    def get(self, request, pk, *args, **kwargs):
        try:
            movie = Movie.objects.get(pk=pk)
            shows = Show.objects.filter(movie=movie)
        except:
            return render(request, "core/movie_detail.html", context={"message": "Not Found"})
        return render(request, "core/movie_detail.html", context={"movie": movie, "shows": shows})


class SendPromotionView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.is_superuser:
            promotions = Promotion.objects.all()
            return render(request, "admin/send_promotion.html", {"promotions":promotions})
        else:
            return HttpResponse('Unauthorized', status=401)

    def post(self, request, *args, **kwargs):
        if request.user.is_superuser:
            promotions = Promotion.objects.all()
            promo_code=request.POST.get("promo_code")
            try:
                users = User.objects.filter(recieve_promotions=True)
            except:
                return render(request, "admin/send_promotion.html", {"message":"NO users to send promo to."})
            email_list = [user.email for user in users]
            try:
                promotion = Promotion.objects.get(promo_code=promo_code)
            except:
                return render(request, "admin/send_promotion.html", {"message":"Promotion does not exist"})
            mail_subject = 'We have new offers just for you!'
            message = render_to_string('core/email_promo_template.html', {
                            "promotion": promotion, 
                        })
            send_mail(mail_subject, message, 'postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org', email_list)
            promotion.is_sent = True
            promotion.save()
            return render(request, "admin/send_promotion.html", {"message":"Promotion sent Successfully", "promotions": promotions})


def filter_title(request, *args, **kwargs):
    if request.POST.get("search"):
        movies = Movie.objects.filter(title__icontains=request.POST.get("search"), is_playing=True)
    else:
        movies = Movie.objects.all()
    if movies:
        return render(request, "core/home.html", context={"movies":movies})
    else:
        return render(request, "core/home.html", context={"message":"No movies"})

def filter_catergory(request, *args, **kwargs):
    if request.POST.get("category"):
        movies = Movie.objects.filter(category=request.POST.get("category"), is_playing=True)
    else:
        movies = Movie.objects.all()
    if movies:
        return render(request, "core/home.html", context={"movies":movies})
    else:
        return render(request, "core/home.html", context={"message":"No movies"})


def filter_rating(request, *args, **kwargs):
    movies = Movie.objects.filter(rating=request.POST.get("rating"), is_playing=True)
    return render(request, "core/home.html", context={"movies":movies})


class SeatListView(View):
    def get(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        show = Show.objects.get(pk=pk)
        seats = Seat.objects.filter(show__pk=pk)
        promotions = Promotion.objects.filter(is_sent=False)
        return render(request, "core/ticket_booking.html", context={"seats":seats, "show":show, "promotions":promotions})


class TicketCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        price=request.POST.get("price")
        row=request.POST.get("row")
        id = request.POST.get("id")
        show = Show.objects.get(pk=id)
        seat, created = Seat.objects.get_or_create(row=row, show=show)
        ticket = Ticket.objects.create(price=price, show=show, seat=seat, user=request.user)
        return render(request, "core/ticket_booking.html", context={"seats":seat, "show":show})


class TicketDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        price=request.POST.get("price")
        row=request.POST.get("row")
        id = request.POST.get("id")
        show = Show.objects.get(pk=id)
        seat = Seat.objects.get(row=row, show=show)
        ticket = Ticket.objects.get(price=price, show=show, seat=seat)
        ticket.delete()
        return render(request, "core/ticket_booking.html", context={"seats":seat, "show":show})


class BookingCreateView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        id = request.POST.get("id")
        show = Show.objects.get(pk=id)
        seats = Seat.objects.filter(show__pk=id)
        tickets = Ticket.objects.filter(user=request.user, show=show)
        total_price = tickets.aggregate(Sum('price'))["price__sum"]
        if request.POST.get("disc_price"):
            discount_price = float(request.POST.get("disc_price"))
            total_price = discount_price
        booking = Booking.objects.create(booking_total=total_price, 
            show=show, no_of_ticket=tickets.count(), user=request.user)
        for ticket in tickets:
            ticket.booking = booking
            ticket.save()
        if settings.BRAINTREE_PRODUCTION:
            braintree_env = braintree.Environment.Production
        else:
            braintree_env = braintree.Environment.Sandbox

        # Configure Braintree
        braintree.Configuration.configure(
            braintree_env,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC_KEY,
            private_key=settings.BRAINTREE_PRIVATE_KEY,
        )

        #fetch cards
        card_num_list = []
        cards = CreditCard.objects.filter(user=request.user)
        for card in cards:
                card_string = asymetric_decrypt_string(card.number, card.private_key)
                card_num_list.append({"number":card_string, "card":card, "id":card.id,"cardName":card.name_on_card,"type":card.type})
        
        #send mail     
        mail_subject = 'Order Confirmed'
        message = render_to_string('core/email_payment_confirmation.html', {
             "total_price": total_price, 
             "user": request.user
        })
        send_mail(mail_subject, message, 'postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org', [request.user.email])
        
        try:
            braintree_client_token = braintree.ClientToken.generate({ "customer_id": user.id })
        except:
            braintree_client_token = braintree.ClientToken.generate({})

        context = {'braintree_client_token': braintree_client_token, "total_price":total_price}
        return render(request, 'core/checkout.html', context={"cards":card_num_list})

            
class GetAllTickets(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        id = request.POST.get("id")
        show = Show.objects.get(pk=id)
        tickets = Ticket.objects.filter(user=request.user, show=show)
        occupied_list = [ticket.seat.row for ticket in tickets]
        return JsonResponse({'occupied_seats': occupied_list})


class PaymentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        nonce_from_the_client = request.POST['paymentMethodNonce']
        total_price = request.POST.get('total_price')
        customer_kwargs = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }
        customer_create = braintree.Customer.create(customer_kwargs)
        customer_id = customer_create.customer.id
        result = braintree.Transaction.sale({
            "amount": total_price,
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })        
        mail_subject = 'Order Confirmed'
        message = render_to_string('core/email_payment_confirmation.html', {
             "total_price": total_price, 
             "user": request.user
        })
        send_mail(mail_subject, message, 'postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org', [request.user.email])
        return HttpResponse('Ok')


class PaymentSuccessView(TemplateView):
    template_name="core/success.html"
