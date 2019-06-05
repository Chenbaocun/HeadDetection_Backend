from time import sleep

from django.test import TestCase
import datetime
from ffmpy import FFmpeg
from queue import Queue
import threading
from Home.test2 import do
# Create your tests here.
# file=open("../UploadVideos/"+"video"+".mp4",'wb+')
# now_time = datetime.datetime.now()
# print(now_time)

# ff = FFmpeg(inputs={'/root/DetectedVideos/input.mp4': None},outputs={'output.mp4': '-vcodec h264 -s 1280*720 -acodec copy -f mp4'})
# print(ff.cmd)


q=Queue(2)

# do()
def duo():
    new_thread = threading.Thread(target=do, name="video_detect")
    q.put(new_thread)
    new_thread.start()
for i in range(5):
    duo()