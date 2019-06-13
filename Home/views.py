import mimetypes
import threading
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from .models import *
from .video_detect import video_detect
from .image_detect import image_detect
import datetime
import simplejson
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
import re
import os
import urllib.parse
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
            print(threading.enumerate())
            if (len(threading.enumerate())>3):
                print("线程已经存在了")
            else:
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
    # 会调用两次
    # print(request.user)
    # print(request.GET.get("filename"))
    user=request.user
    filename=request.GET.get("filename")
    path='/root/DetectedVideos_AVC/'+str(user)+"###"+str(filename)
    return stream_video(request,path)


def login_app(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        # print(username)
        # print(password)
        user=authenticate(username=username, password=password)
        # print(user)
        if user :
            return HttpResponse(username)#验证成功
        else:
            return HttpResponse(0)#账号或者密码错误

def count_app(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        count = request.POST.get('count')
        mobiletype=request.POST.get('mobiletype')
        date=datetime.datetime.now()
        a=OnlineUser.objects.filter(username=username,online=1)
        target=a[0].target
        print(target)
        # print(username)
        # print(count)
        # print(mobiletype)
        RealtimeCount.objects.create(username=username,count=count,mobiletype=mobiletype,date=date,location=target)
        return HttpResponse(1)
def abnormal_image(request):
    if request.method=='POST':
        # username=request.POST.get('username')
        abnormal_image=request.FILES.get('img')
        username=str(abnormal_image).split("###")[0]
        # print(abnormal_image)
        file = open("/root/AbnormalImage/" + str(abnormal_image), "wb+")
        a=OnlineUser.objects.filter(username=username,online=1)
        AbnormalImage.objects.create(username=username,filename=str(abnormal_image),hascalculated=0,location=a[0].target)
        for chunk in abnormal_image.chunks():
            file.write(chunk)
        file.close()
        print("异常图片请求发现线程总数："+str(threading.enumerate()))
        if (len(threading.enumerate()) > 3):
            print("线程已经存在了")
        else:
            new_thread = threading.Thread(target=image_detect, name="image_detect", args=(
                "/root/AbnormalImage/" + str(abnormal_image), "/root/DetectedImage/" + str(abnormal_image).split(".")[0]+".jpg", str(abnormal_image), username,))
            new_thread.start()
        return HttpResponse(1)

def get_threshold(request):
    if request.method=="POST":
        username=request.user
        ret=NumThreshold.objects.filter(username=username)
        if (ret):
            for i in ret:
                return HttpResponse(i.threshold)
        else:
            return HttpResponse()

def set_threshold(request):
    if request.method=="POST":
        username=request.user
        threshold=request.POST.get('threshold_update')
        ret=NumThreshold.objects.filter(username=username)
        if (ret):
            NumThreshold.objects.filter(username=username).update(threshold=threshold)
            return HttpResponse(1)
        else:
            NumThreshold.objects.create(username=username,threshold=threshold)
            return HttpResponse(1)
        return HttpResponse()#前两个if都不通

def get_threshold_app(request):
    if request.method=='POST':
        username=request.POST.get("username")
        startCount=request.POST.get('startCount')
        if(startCount=='1'):
            a=OnlineUser.objects.filter(username=username)
            if(a):
                OnlineUser.objects.filter(username=username).update(online=1)
            else:
                OnlineUser.objects.create(username=username,online=1)
        ret = NumThreshold.objects.filter(username=username)
        if ret:
            for i in ret:
                return HttpResponse(i.threshold)
        else:
            return HttpResponse(0)

def set_threshold_app(request):
    if request.method=='POST':
        username=request.POST.get("username")
        threshold = request.POST.get('threshold')
        ret = NumThreshold.objects.filter(username=username)
        if (ret):
            NumThreshold.objects.filter(username=username).update(threshold=threshold)
            return HttpResponse(1)
        else:
            NumThreshold.objects.create(username=username, threshold=threshold)
            return HttpResponse(1)
        return HttpResponse()  # 前两个if都不通
def up_advice(request):
    if request.method == 'POST':
        username=request.user
        advice=request.POST.get('up_advice')
        Useradvice.objects.create(username=username,advice=advice)
        return HttpResponse(1)

def real_time_count(request):
    if request.method == 'POST':
        username = request.user
        b=OnlineUser.objects.filter(username=username,online=1)
        c=NumThreshold.objects.filter(username=username)
        threshold=c[0].threshold
        # print(b)
        if b:
            a = RealtimeCount.objects.filter(username=username)
            real_time_count = a[len(a) - 1].count
            # print(real_time_count)
            red=0
            if int(real_time_count)>int(threshold):
                red=1
            content={"real_time_count":real_time_count,"red":red}
            return HttpResponse(simplejson.dumps(content))
        else:
            return HttpResponse(-1)

def exit_count_app(request):
    if request.method=='POST':
        username=request.POST.get('username')
        OnlineUser.objects.filter(username=username).update(online=0)
        return HttpResponse(0)


def get_TotalOnlineUser(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        a=OnlineUser.objects.filter(username=username,online=1)
        return HttpResponse(len(a))
    else:
        return HttpResponse(-1)

def getAbnormalImageList(request):
    if request.method=='POST':
        user=request.user
        queryResult = AbnormalImage.objects.filter(username=user)
        context=[]
        for i in queryResult:
            a=Targetname.objects.filter(num=i.location)
            row = {}
            row['date']=i.filename.split('###')[1].split(".")[0]
            row['filename']=str(i.filename).split('###')[1]
            row['result']=i.result
            row['target']=a[0].target
            if i.hascalculated=='1':
                row['status']='计算完成'
            else:
                row['status']='排队计算中..'
            context.append(row)
        context={"data":context}
        # print(context)
        return HttpResponse(simplejson.dumps(context))

def image_play(request):
    username = request.user
    filename = request.GET.get("filename")
    filename = urllib.parse.unquote(filename)
    # print(filename)
    path = '/root/DetectedImage/' + str(username) + "###" + str(filename.split('.')[0]+".jpg")
    with open(path, 'rb') as f:
        image_data = f.read()
    return HttpResponse(image_data, content_type='image/jpg')


def getHistory(request):
    if request.method=='POST':
        username = request.user
        queryResult = RealtimeCount.objects.filter(username=username)
        context=[]
        for i in queryResult:
            row = {}
            row['date']=i.date
            row['count']=i.count
            context.append(row)
        context={"data":context}
        # print(context)
        return HttpResponse(simplejson.dumps(context))

def setTarget_app(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        target=request.POST.get("target")
        a=OnlineUser.objects.filter(username=username)
        if a:
            OnlineUser.objects.filter(username=username).update(target=target)
        else:
            OnlineUser.objects.filter(username=username,online=0,target=target)
        return HttpResponse(1)

def getTarget(request):
    if request.method == 'POST':
        username = request.user
        a=OnlineUser.objects.filter(username=username,online=1)
        if a:
            b = Targetname.objects.filter(num=a[0].target)
            return HttpResponse(b[0].target)
        else:
            return HttpResponse()

def image_play_app(request):
    num = request.GET.get("num")
    username=request.GET.get("username")
    num=urllib.parse.unquote(num)
    username = urllib.parse.unquote(username)
    a=AbnormalImage.objects.filter(hascalculated=1)
    filename=a[int(num)].filename
    # print(filename)
    path = '/root/DetectedImage/' + str(username) + "###" + str(filename.split('.')[0] + ".jpg")
    with open(path, 'rb') as f:
        image_data = f.read()
    return HttpResponse(image_data, content_type='image/jpg')

