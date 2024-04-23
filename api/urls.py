

from django.urls import path

from . import views


urlpatterns = [
    path('auth/get_me', views.GetMeView.as_view(), name='get_me'),
    path('auth/login', views.LoginView.as_view(), name='login'),
    path('auth/register', views.RegisterView.as_view(), name='register'),
    path('auth/logout', views.LogoutView.as_view(), name='logout'),
]
