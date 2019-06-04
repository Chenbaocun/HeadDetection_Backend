import mimetypes
import threading
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from .video_detect import video_detect
import datetime
import simplejson
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
import re
import os
# Create your views here.
def Index(request):
    if request.method == 'POST':
        session_key=request.session.session_key
        a = request.session.exists(session_key)#在db中验证
        if(a):
            # print(request.user)#用户名
            # print(request.session.get('_auth_user_id'))  # 获取用户ID
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
        # print("从数据库中查到了"+a)
        if(a):
            # 否则还是认为是成功了
            return HttpResponse('this file you have uploded!!',status=500)
        else:
            Uploadvideos.objects.create(username=request.user,hascalculated=0,uploaddate=str(datetime.datetime.now()),filename=filename)
            # print(obj.name)
            if not obj:
                return HttpResponse('no files for upload')
            # 在Linux上从这访问上一级是一个.
            file = open("/root/UploadVideos/" + filename, "wb+")
            for chunk in obj.chunks():
                file.write(chunk)
            file.close()
            new_thread = threading.Thread(target=video_detect, name="video_detect", args=(
            "/root/UploadVideos/" + filename, "/root/DetectedVideos/" + filename, filename, request.user,))
            new_thread.start()
            return HttpResponse("upload success")
def beforeUploadVideo(request):
    if request.method=='POST':
        filename=request.POST.get('filename')
        filename=str(request.user)+"###"+str(filename)
        a = Uploadvideos.objects.filter(filename=filename,username=request.user)
        # print("从数据库中查到了"+a)
        if(a):
            # 否则还是认为是成功了
            return HttpResponse(1)
        else:
            return HttpResponse()

def myupload(request):
    if request.method=='POST':
        user=request.user
        queryResult = Uploadvideos.objects.filter(username=user)
        context=[]
        for i in queryResult:
            row = {}
            row['date']=i.uploaddate
            row['filename']=str(i.filename).split('###')[1]
            if i.hascalculated=='1':
                row['status']='计算完成'
            else:
                row['status']='排队计算中..'
            context.append(row)
        context={"data":context}
        # print(context)
        return HttpResponse(simplejson.dumps(context))

def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data

def stream_video(request, path):
    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 8       # 8M 每片,响应体最大体积
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206, content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp
def video_play(request):
    username=request.user
    print(request.GET.get("filename"))
    return stream_video(request,'/root/UploadVideos/chenbaocun###13.mp4')