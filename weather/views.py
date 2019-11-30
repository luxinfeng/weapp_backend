from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import os

global city_id
with open('weather/city_id.json', 'rb') as load_city_id:
    city_id = json.load(load_city_id)


def find(city_list=city_id,key="city_name",value="null"):
    value = value.replace('市','')
    for i ,dic in enumerate(city_id):
        if dic[key] == value:
            return i




def getCITYID(city=""):
    position = find(value=city)
    if city_id[position].get('city_code')!= "":
        return city_id[position].get('city_code')


def getCITYWEATHER(request):
    if request.method == 'POST':
        data = request.POST
        try:
            local_cityid = getCITYID(data['local_city'])
        except Exception as error:
            print('获取前端传回的数据失败')
            print(error)
        url = "http://t.weather.sojson.com/api/weather/city/%s"% local_cityid
#        url = "http://t.weather.sojson.com/api/weather/city/101030100"
        response = requests.request('GET',url)
        local_city_weather = eval(response.content)
        data = {
            "code": 200,
            "msg": "success",
            "weather": local_city_weather.get('data').get('forecast')[0].get('type'),
            "temperature": local_city_weather.get('data').get('wendu'),
            "humidity": local_city_weather.get('data').get('shidu'),
            "air_quality": local_city_weather.get('data').get('quality'),
            "fengli": local_city_weather.get('data').get('forecast')[0].get('fl')
        }
        print(type(data))
        return HttpResponse(json.dumps(data,ensure_ascii=False),content_type="application/json",charset="utf-8",status="200",reason='success')
    else:
        return HttpResponse('It is not a POST request!')


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
