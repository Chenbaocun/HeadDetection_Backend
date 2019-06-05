from django.test import TestCase
import datetime
from ffmpy import FFmpeg
# Create your tests here.
# file=open("../UploadVideos/"+"video"+".mp4",'wb+')
now_time = datetime.datetime.now()
print(now_time)

ff = FFmpeg(inputs={'/root/DetectedVideos/input.mp4': None},outputs={'output.mp4': '-vcodec h264 -s 1280*720 -acodec copy -f mp4'})
print(ff.cmd)