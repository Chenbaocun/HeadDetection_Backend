"""HeadDetection_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from Home import views
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('',TemplateView.as_view(template_name="index.html")),
    path('login/',views.login),
    path('login_app/', views.login_app),
    path('Index/', views.Index),
    path('Logout/', views.Logout),
    path('register/', views.register),
    path('beforeUploadVideo/', views.beforeUploadVideo),
    path('UploadVideo/', views.UploadVideo),
    path('myupload/', views.myupload),
    path('video_play/',views.video_play),
    path('count_app/',views.count_app),
    path('abnormal_image/',views.abnormal_image),
    path('get_threshold/', views.get_threshold),
    path('set_threshold/', views.set_threshold),
    path('get_threshold_app/', views.get_threshold_app),
    path('set_threshold_app/', views.set_threshold_app),
    path('up_advice/', views.up_advice),
    path('real_time_count/', views.real_time_count),
    path('exit_count_app',views.exit_count_app)

]