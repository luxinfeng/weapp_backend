from django.shortcuts import render
import requests
import json
from django.http import HttpResponse
#from login.models import User
from login import models

from django.utils import timezone
# Create your views here.


class OpenidUtils(object):
    def __init__(self, jscode):
        self.url = "https://api.weixin.qq.com/sns/jscode2session"
        self.appid = 'wx2586b5b5c8eedb85'
        self.secret = '2ef49290977f6dff67be611a497c5c60'
        self.jscode = jscode    # 前端传回的动态jscode

    def get_openid(self):
        url = self.url + "?appid=" + self.appid + "&secret=" + self.secret + "&js_code=" + self.jscode + "&grant_type=authorization_code"
        r = requests.get(url)
        openid = r.json()['openid']
        return openid



def user_login(request):
    if request.method == 'POST':
        data = request.POST
        try:
            openid_user = OpenidUtils(data['code'])
            userName = openid_user.get_openid()
        except Exception as error:
            print('获取前端传回的数据失败')
            print(error)
#    params = request.data
#    openid_user = OpenidUtils(params.get('code'))
#    userName = openid_user.get_openid()
#    userInfo = params.get('userinfo')
    try:
        user = models.User.objects.get(username=userName)
    except Exception as e:
        user = None
    if user:
        # 更新用户信息
        user = models.User.objects.get(username=userName)
        print(userName)
    else:
        # 注册新用户
        current_time = timezone.now()
        user = models.User.objects.create(username=userName,user_times=5,created_date=current_time)
        # 手动生成JWT
    # 手动生成token验证
    user_times = user.user_times

#    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#    payload = jwt_payload_handler(user)
#    token = jwt_encode_handler(payload)

    ret = {'code': '00000', 'msg': None, 'token':userName,'times':user_times}

    ret['msg'] = '授权成功'
    return HttpResponse(json.dumps(ret, ensure_ascii=False), content_type="application/json", charset="utf-8",
                        status="200", reason='success')
    return JsonResponse(ret)

