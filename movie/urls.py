from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('detail/<int:pk>', views.MovieDetailView.as_view(), name='detail'),
    path('seat_list/<int:pk>', views.SeatListView.as_view(), name="seat_list"),
    path('send_promotion', views.SendPromotionView.as_view(), name='sendpromotion'),
    path('filter_title', views.filter_title, name="filter_title"),
    path('filter_category', views.filter_catergory, name="filter_category"),
    path('filter_rating', views.filter_rating, name="filter_rating"), 
    path('ticket_create', views.TicketCreateView.as_view(), name="ticket_create"),
    path('ticket_delete', views.TicketDeleteView.as_view(), name="ticket_delete"),
    path('create-checkout-session', views.BookingCreateView.as_view(), name="create-checkout-session"),
    path('get_booking', views.GetAllTickets.as_view(), name="get_booking"),
    path('payment', views.PaymentView.as_view(), name='payment'),
    path('payment_successful', views.PaymentSuccessView.as_view(), name="payment_sucessful")
]