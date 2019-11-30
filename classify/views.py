from django.shortcuts import render
from django.http import HttpResponse,HttpResponseForbidden
import classify.models as MODEL
import requests
import json
import os
import torch
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
from torchvision import datasets, models, transforms
import numpy
from weapp import settings
from django.http import FileResponse, JsonResponse
import time
from login.models import User
import pretrainedmodels
from PIL import Image

global openid_user
device = torch.device('cpu')

idx_to_class = {
    0:'其它',
    1:'卷云',
    2:'卷层云',
    3:'卷积云',
    4:'层云',
    5:'层积云',
    6:'积云',
    7:'积雨云',
    8:'雨层云',
    9:'高层云',
    10:'高积云'
}

image_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(size=256, scale=(0.8, 1.0)),
        transforms.RandomRotation(degrees=15),
        transforms.RandomHorizontalFlip(),
        transforms.CenterCrop(size=224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ]),
    'valid': transforms.Compose([
        transforms.Resize(size=256),
        transforms.CenterCrop(size=224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ]),
    'test': transforms.Compose([
        transforms.Resize(size=256),
        transforms.CenterCrop(size=224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])
}

model = pretrainedmodels.resnet18()
model.last_linear = nn.Sequential(
    nn.Linear(model.last_linear.in_features,256),
    nn.ReLU(),
    nn.Dropout(0.4),
    nn.Linear(256,11),
    nn.LogSoftmax(dim=1))
#model.cuda()
loss_criterion = nn.NLLLoss()
optimizer = optim.Adam(model.parameters(),lr=0.0003)
model.load_state_dict(torch.load('classify/class_model/100-fold.pth', map_location=device))


def predict(model, test_image_name):
    '''
    Function to predict the class of a single test image
    Parameters
        :param model: Model to test
        :param test_image_name: Test image

    '''

    transform = image_transforms['test']

    test_image = Image.open(test_image_name)

    test_image_tensor = transform(test_image)

    if torch.cuda.is_available():
        test_image_tensor = test_image_tensor.view(1, 3, 224, 224).cuda()
    else:
        test_image_tensor = test_image_tensor.view(1, 3, 224, 224)

    with torch.no_grad():
        model.eval()
        # Model outputs log probabilities
        out = model(test_image_tensor)
#        print(out)
        ps = torch.exp(out)
#        print(ps)
        topk, topclass = ps.topk(1, dim=1)
        topclass = topclass.numpy()[0][0]
        pic_class = idx_to_class[topclass]
#        print(type(topclass))
#        print(type(pic_class))
        return pic_class,str(topclass)


def user_auth(request):
    global openid_user
    if request.method == 'POST':
        data = request.POST
        try:
            openid_user = data['code']
            if openid_user == '':
                openid_user = 'init'
            print(openid_user)
            return HttpResponse(content_type="application/json", charset="utf-8",
                            status="200", reason='success')
        except Exception as error:
            print('获取前端传回的数据失败')
            print(error)
            return HttpResponse(content_type="application/json",charset="utf-8",status="200",reason='unlog')

def init_user(request):
#    if request.method == 'POST':
    global openid_user
    openid_user = "init"
    return HttpResponse(content_type="application/json", charset="utf-8",
                        status="200", reason='success')



def getPICTURE(request):
    global openid_user
    files = request.FILES
    if openid_user != 'init':
        user = User.objects.get(username=openid_user)     ##用户登陆/剩余次数判断
        times = user.user_times
    else:
        return HttpResponseForbidden()
    if times < 0:
#    if 1:
        times = times - 1
        print(times)
        User.objects.filter(username=openid_user).update(user_times=times)
        for key, value in files.items():
            content = value.read()
    #        md5 = hashlib.md5(content).hexdigest()
            name = str(time.time())[:10]
            path = os.path.join(settings.IMAGES_DIR, name+".jpg")
            with open(path, "wb") as f:
                f.write(content)
            result, class_idx = predict(model, path)
            MODEL.USER_PIC.objects.create(user=openid_user,pic=name,result=class_idx)
#            result_json = json.loads(result)
#            class_idx_json = json.loads(class_idx)
            data = class_idx
#        return HttpResponse(json.dumps(data,ensure_ascii=False),content_type="application/json",charset="utf-8",status="200", reason='success')
        return HttpResponse(data,content_type="application/json",charset="utf-8",status="200",reason='success')
    else:
        return HttpResponseForbidden()
#        return HttpResponse(content_type="application/json",charset="utf-8",status="404",reason='unlog')
