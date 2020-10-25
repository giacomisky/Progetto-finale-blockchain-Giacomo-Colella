from django.urls import path
from . import views
from managing.views import getWordOnSite, getUpdate

urlpatterns = [
    path("", views.homePage, name="homePage"),
    path("login/", views.login, name='login'),
    path("logout/", views.log_out, name='log_out'),
    path("registration/", views.registration, name='registration'),
    path("adminPanel", views.adminPanel, name='adminPanel')
]