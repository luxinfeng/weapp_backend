from django.urls import path

from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/get_city_id', views.getCITYID, name='getcityid'),
    path('api/get_city_weather', views.getCITYWEATHER, name='getcityweather')
]


