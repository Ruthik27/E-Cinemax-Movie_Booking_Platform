from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
     
    path('seat', views.BookingListView.as_view(), name='seat'),
    path('booking_history', views.BookingHistoryListView.as_view(), name='bookig_history')

]