from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.homePage, name="homePage"),
    path("checkAuct/", views.checkAuct, name="checkAuct"),
    path("login/", views.login, name='login'),
    path("logout/", views.log_out, name='log_out'),
    path("registration/", views.registration, name='registration'),
    path("adminPanel", views.adminPanel, name='adminPanel')
]


