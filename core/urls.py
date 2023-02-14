from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
     
    path('', views.HomeView.as_view(), name='home'),
    path('login', views.LoginEmailView.as_view(), name='login'),
    path('signup', views.SignupView.as_view(), name='signup'),
    path('verify_email', views.VerifyEmailView.as_view(), name='verify_email'),
    path('forgot_password', views.ResetPasswordView.as_view(), name='forgot_password'),
    path('reset_password', views.ChangePasswordView.as_view(), name='reset_password'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('activate/?P<str:uidb64>/?P<str:token>', views.activate, name='activate'),
    path('password_reset_confirmation/?P<str:uidb64>/?P<str:token>', views.change_password, name='reset_confirm'),
    path('password_reset_complete', views.ChangeUserPassword.as_view(), name='password_reset_complete'),
    path('update_card/?P<int:pk>', views.UpdateCreditCard.as_view(), name="update_card"),
    path('edit_password', views.EditPassword.as_view(), name="edit_password"),
    path('verify_password', views.CheckPassword.as_view(), name="verify_password"),
    path("credit_card/create", views.CreateCreditCard.as_view(), name="credit_card"),
    path("user/profile", views.GetUserProfile.as_view(), name="user_profile"),
    path('cancel/', views.CancelView.as_view(), name='cancel'),
    path('success/', views.SuccessView.as_view(), name='success'),

]
