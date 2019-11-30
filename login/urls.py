from django.urls import path

from . import views

app_name = 'login'

urlpatterns = [
    path('api/user_login', views.user_login, name='user_login'),
]