# -*- coding: utf-8 -*-
# @Time : 2019/6/5 18:34
# @Author : Tom Chen
# @Email : chenbaocun@emails.bjut.edu.cn
# @File : test2.py
# @Software: PyCharm
from time import sleep
# from Home.tests import q

def do():
    sleep(2)
    # print(1)
    file=open('./queue.txt','w+')
    # print(file.read())
    file.write('1')
    file.close()
    # q.get()
do()