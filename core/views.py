from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils import encoding
from django.views.generic import View, TemplateView, CreateView
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout, get_user_model
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from core.models import User 
from card.models import CreditCard
from movie.models import Movie

import base64
import uuid
import os
from passlib.hash import sha256_crypt
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import secrets
import smtplib, ssl
import requests

key = Fernet.generate_key()
# Create your views here.
fernet = Fernet(key)


def create_asymetric_public_and_private_keys_as_string():

    """
    creates and returns a public key and a private key as string values
    """

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()

    # Save key to string
    serial_private_as_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    serial_public_as_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    serial_private_as_string = serial_private_as_bytes.decode("utf-8")
    serial_public_as_string = serial_public_as_bytes.decode("utf-8")

    return serial_public_as_string, serial_private_as_string


def asymetric_encrypt_string(stringToEncrypt, publicKeyAsString):
    """
    Encrypts a string with public key as string
    """
    # convert public key from string to bytes
    keyAsBytes = bytes(publicKeyAsString, "utf-8")
    public_key_to_use = serialization.load_pem_public_key(
        keyAsBytes, backend=default_backend()
    )

    # convert text to bytes
    textToEncryptAsBytes = bytes(stringToEncrypt, "utf-8")

    # encrypt text
    encryptedBytes = public_key_to_use.encrypt(
        textToEncryptAsBytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # CONVERSION of raw bytes to BASE64 representation
    encryptedString = base64.urlsafe_b64encode(encryptedBytes)

    return encryptedString.decode("utf-8")


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



class HomeView(View):

    def get(self, request, *args, **kwargs):
        movies = Movie.objects.filter(is_playing=True)
        now_playing_image_list = [movie.poster_image for movie in movies]
        now_playing_id_list = [movie.id for movie in movies]
        now_playing_title_list = [movie.title for movie in movies]

        upcoming_movies = Movie .objects.filter(is_playing=False)
        upcoming_image_list = [movie.poster_image for movie in upcoming_movies]
        upcoming_id_list = [movie.id for movie in upcoming_movies]
        upcoming_title_list = [movie.title for movie in upcoming_movies]
        return render(
            request, 'core/home.html', 
            context={"now_playing_image_list": now_playing_image_list, 
                     "now_playing_id_list": now_playing_id_list,
                     "now_playing_title_list": now_playing_title_list,
                     "upcoming_image_list": upcoming_image_list,
                     "upcoming_id_list": upcoming_id_list,
                     "upcoming_title_list": upcoming_title_list,
                     "movies": movies,
                     "upcoming_movies": upcoming_movies 
                    }
            )


class SignupView(TemplateView):
    template_name='core/signup.html'
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        username = request.POST.get('username')
        address = request.POST.get('address')
        recieve_promotions = request.POST.get('promobox')
        if recieve_promotions == 'on':
            recieve_promotions = True
        else:
            recieve_promotions = False
        password = make_password(request.POST.get('password'))
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=username)
            if user:
                return render(request,'core/signup.html', context={'message': 'This username is already taken'})
        except:
            pass
        try:
            user = User.objects.get(email=email)
            if user:
                return render(request, 'core/signup.html', context={'message': 'This email is already taken'})
        except:
            pass

        user = User.objects.create(username=username, first_name=first_name, 
            last_name=last_name, password=password, email=email, is_active=False, recieve_promotions=recieve_promotions, address= address)
        if user:
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('core/email_template.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                send_mail(mail_subject, message, 'postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org', [email])
                #requests.post("https://api.mailgun.net/v3/sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org",auth=("api", "7c0e00bf9c31492b4d9790bb82a41f00-31eedc68-8cc7ca31"),data={"from": "Excited User <mailgun@YOUR_DOMAIN_NAME>","to": ["abhijeet18t@gmail.com", "YOU@YOUR_DOMAIN_NAME"],"subject": "Hello","text": "Testing some Mailgun awesomness!"})
                return render(request,'core/signup.html', context={'message': 'User has been succesfully created, please verify your email.'})
                

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request,'core/email_confirmation.html', context={'message':'Confirmation successful'})
    else:
        return HttpResponse('Activation link is invalid!')


class VerifyEmailView(TemplateView):
    template_name='core/verify_email.html'


class LoginEmailView(TemplateView):
    template_name='core/login.html'

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            return render(request,'core/login.html', context={'message':'Incorrect username or password1'})
        if user is not None:
            if user.is_active:
                try:
                    user = authenticate(request, username=username, password=password)
                    login(request, user)
                    return redirect(reverse('home'))
                except:
                    return render(request,'core/login.html', context={'message':'Incorrect username or password'})
            else:
               return render(request,'core/login.html', context={'message':'Incorrect username or password'}) 
        else:
            return render(request,'core/login.html', context={'message':'Incorrect username or password'})


class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name='core/reset_password.html'
    

class ResetPasswordView(TemplateView):
    template_name='core/forgot_password.html'
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except:
            return render(request, 'core/forgot_password.html', contex={'message': 'This email does not exist,Please check Your email'})

        if user:
                current_site = get_current_site(request)
                mail_subject = 'Reset Password'
                message = render_to_string('core/password_reset_email.html', {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        })
                send_mail(mail_subject, message, 'postmaster@sandbox92b2fca3c3f8430395f64f4d5f469413.mailgun.org', [email])
        return render(request,'core/reset_password.html', context={'message': 'User has been succesfully created, please verify your email.'})



def change_password(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        return render(request,'core/change_password.html', context={'email': user.email})
    else:
        return HttpResponse('Activation link is invalid!')


class ChangeUserPassword(View):

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password') 

        if new_password == confirm_new_password:
            user = User.objects.get(email=email) 
            user.password = make_password(new_password)
            user.save()
            return render(request, 'core/password_reset_complete.html')


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('home'))


class GetUserProfile(LoginRequiredMixin, View):
    
    
    def get(self, request, *args, **kwargs):
        user = request.user
        card_num_list = []
        try:
            cards = CreditCard.objects.filter(user=user)
            for card in cards:
                last_4_decrypted_card_num = asymetric_decrypt_string(card.number, card.private_key)[12:]
                card_string = '**** **** ****' + ' ' + last_4_decrypted_card_num
                card_num_list.append({"number":card_string, "card":card, "id":card.id})
        except:
            return render(request, 'core/profile.html', context={ "message":"Cannot fetch user profile data!"})

        return render(
            request, 'core/profile.html', 
            context={
                "email":user.email, 
                "username": user.username, 
                "first_name":user.first_name, 
                "last_name": user.last_name,
                "address":user.address,
                "credit_cards": card_num_list,
                }
            )
    
    def post(self, request, *args, **kwargs):
        card_num_list = []
        user = User.objects.get(email=request.user.email)
        if request.POST.get('username') and request.POST.get('username')!= "":
            user.username = request.POST.get('username')
        
        if request.POST.get('first_name') and request.POST.get('first_name')!= "" :
            user.first_name = request.POST.get('first_name')
        
        if request.POST.get('last_name') and request.POST.get('last_name')!= "":
            user.last_name = request.POST.get('last_name')

        if request.POST.get('address') and request.POST.get('address')!= "":
            user.address = request.POST.get('address')
    
        user.save()
        cards = CreditCard.objects.filter(user=user)
        for card in cards:
            last_4_decrypted_card_num = asymetric_decrypt_string(card.number, card.private_key)[12:]
            card_string = '**** **** ****' + ' ' + last_4_decrypted_card_num
            card_num_list.append({"number":card_string, "card":card, "id":card.id})

        return render(request, "core/profile.html", 
             context={
                "username":user.username, 
                "email":user.email,
                "first_name":user.first_name, 
                "last_name": user.last_name,
                "credit_cards": card_num_list,
                "address":user.address,  
                "message": "your profile has been updated"
                })


class CreateCreditCard(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
            return render(request, "core/add_card.html")

    def post(self, request, *args, **kwargs):
        user = request.user
        public_key, private_key = create_asymetric_public_and_private_keys_as_string()
        card_number = asymetric_encrypt_string(request.POST.get('card_number'), public_key)
        name_on_card = request.POST.get('card_name')
        expiration_date = request.POST.get('expiration_date')
        card_type = request.POST.get('card_type')
        billing_address = request.POST.get('billing_address')
        

        try:
           cards = CreditCard.objects.filter(user=user)
           if  cards.count() >= 3:
               return render(request, "core/add_card.html", context={"message": "You have already added 3 cards. You can't add more than 3"})
        except:
            pass

        CreditCard.objects.create(
            user=user, number=card_number, 
            name_on_card=name_on_card, 
            expiration_date=expiration_date,
            type=card_type,
            billing_address=billing_address,
            public_key = public_key,
            private_key = private_key
            )
        return render(request, "core/add_card.html", {"message": "Your card has been added."})


class CheckPassword(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "core/check_old_password.html")
    

    def post(self, request, *args, **kwargs):
        user = request.user
        password = request.POST.get('password')
        if user.check_password(password):
            return render(request, "core/change_user_password.html")
        else:
            return render(request, "core/check_old_password.html", conetxt={"message": "Incorrect Password."})


class EditPassword(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "core/change_user_password.html")
    def post(self, request, *args, **kwargs):
        user = request.user
        password = request.POST.get('old_password')
        if user.check_password(password):
            new_password = request.POST.get('new_password')
            confirm_passsword = request.POST.get('confirm_password')
            if confirm_passsword == new_password:
                user.password = make_password(new_password)
                user.save()
                return render(request, "core/change_user_password.html", context={"message": "Password sucessfully changed"})
            return render(request, "core/change_user_password.html",context={"message": "Password did not match"})
        else:
            return render(request, "core/change_user_password.html", context={"message": "Incorrect Password."})


class UpdateCreditCard(LoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        card = CreditCard.objects.get(pk=pk)
        last_4_decrypted_card_num = asymetric_decrypt_string(card.number, card.private_key)[12:]
        card_string = '**** **** ****' + ' ' + last_4_decrypted_card_num
        return render(request, "core/edit_card.html", context={"card_name":card.name_on_card, "card_number":card_string,
            "card_type":card.type, "card_expiration_date": card.expiration_date, "card_billing_address":card.billing_address, 
                "id":card.id})

    def post(self, request, pk, *args, **kwargs):
        try:
            card = CreditCard.objects.get(pk=pk)
        except:
            return render(request, "core/update_card.html", context={"message": "Cant fetch this card"})
        if request.POST.get('card_number') and request.POST.get('card_number')!= "":
            card.number = request.POST.get('card_number')
        
        if request.POST.get('card_name') and request.POST.get('card_name')!= "" :
            card.name_on_card = request.POST.get('card_name')
        
        if request.POST.get('type') and request.POST.get('type')!= "":
            card.type = request.POST.get('type')

        if request.POST.get('expiration_date') and request.POST.get('expiration_date')!= "":
            card.expiration_date = request.POST.get('expiration_date')

        if request.POST.get('billing_address') and request.POST.get('billing_address')!= "":
            card.billing_address = request.POST.get('billing_address')

        card.save()
        return render(request, "core/edit_card.html", 
        context={"card_name":card.name_on_card, "card_number":card.number,
            "card_type":card.type, "card_expiration_date": card.expiration_date, "card_billing_address":str(card.billing_address), 
                "id":card.id, "message": "your card has been updated"})


class SuccessView(TemplateView):
    template_name = "core/success.html"

class CancelView(TemplateView):
    template_name = "core/cancel.html"