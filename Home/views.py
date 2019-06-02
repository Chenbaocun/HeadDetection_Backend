import threading
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from .video_detect import video_detect
import datetime
# Create your views here.
def Index(request):
    if request.method == 'POST':
        session_key=request.session.session_key
        a = request.session.exists(session_key)#在db中验证
        if(a):
            print(request.user)#用户名
            print(request.session.get('_auth_user_id'))  # 获取用户ID
            return HttpResponse(str(request.user))
        else:
            return HttpResponse()


def login(request):
    if request.method=='POST':
        # print(request.POST)
        username=request.POST.get('username')
        password=request.POST.get('password')
        # print("UserNum:"+str(username))
        # print("PassWord:"+str(password))
        user=authenticate(username=username, password=password)
        if user and user.is_authenticated:
            auth.login(request,user)#登录并且存储sessionid
            # auth.logout(request)#
            return HttpResponse(username)#验证成功
        else:
            return HttpResponse(0)#账号或者密码错误
    return HttpResponse(2)#不是post请求
def Logout(request):
    auth.logout(request)
    return HttpResponse(1)
def register(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        gender=request.POST.get('gender')
        birthdate=request.POST.get('birthDate')
        edudegree=request.POST.get('eduDegree')
        email=request.POST.get('email')
        usertages=request.POST.get('UserTags')
        print(str(username)+"|"+str(password)+"|"+str(gender)+"|"+str(birthdate)+"|"+str(edudegree)+"|"+str(email)+"|"+str(usertages))
        user = User.objects.filter(username=username)
        if user:
            # 用户名已经被占用
            print("用户名已经被占用")
            return HttpResponse(2)
        else:
            User.objects.create_user(username=username,email=email,password=password)
            return HttpResponse(1)#注册成功


# 上传文件
def UploadVideo(request):
    if request.method=='POST':
        obj=request.FILES.get('upload_video')
        filename=str(request.user)+"###"+str(obj.name)
        a = Uploadvideos.objects.filter(filename=filename,username=request.user)
        print("从数据库中查到了"+a)
        if(a):
            # 否则还是认为是成功了
            return HttpResponse('this file you have uploded!!',status=500)
        else:
            Uploadvideos.objects.create(username=request.user,hascalculated=0,uploaddate=str(datetime.datetime.now()),filename=filename)
        # print(obj.name)
    if not obj:
        return HttpResponse('no files for upload')
    # 在Linux上从这访问上一级是一个.
    file=open("/root/UploadVideos/"+filename,"wb+")
    for chunk in obj.chunks():
        file.write(chunk)
    file.close()
    new_thread = threading.Thread(target=video_detect, name="video_detect", args=("/root/UploadVideos/"+filename,"/root/DetectedVideos/"+filename,filename,request.user,))
    new_thread.start()
    return HttpResponse("upload success")