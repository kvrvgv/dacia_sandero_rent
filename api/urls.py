

from django.urls import path

from . import views


urlpatterns = [
    path('auth/get_me', views.GetMeView.as_view(), name='get_me'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),

    path('available_transport', views.AvailableTransport.as_view(), name='available_transport'),
    path('available_plans', views.AvailablePlans.as_view(), name='available_plans'),
    path('start_ride', views.StartRide.as_view(), name='start_ride'),
    path('end_ride', views.EndRide.as_view(), name='end_ride'),
]
