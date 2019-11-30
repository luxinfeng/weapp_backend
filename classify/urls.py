from django.urls import path

from . import views

app_name = "classify"

urlpatterns = [
    path('api/get_picture', views.getPICTURE, name='getpicture'),
    path('api/user_auth',views.user_auth,name='user_auth'),
    path('api/init_user',views.init_user,name='init_user'),
]