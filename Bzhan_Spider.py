"""
!/usr/bin/env python3
-*- coding: utf-8 -*-
@Date    : 2018-04-11 20:38:32
@Author  : zhangcaocao (zhangcaocao66@gmail.com)
@Link    : http://little-rocket.cn/
"""

import platform
import queue
import random
import re
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import requests
import sympy

Img_Url = []
Image_url_num = 1
name = 0
exitFlag = 0
get_source_flag = 0
page_num = 0
workQueue = queue.Queue(10)
page_all_num = 100   # 所需要爬取的页数。

def Help():
    print('python_version: '.format(platform.python_version()))


def LoadUserAgents(uafile):
    """
    uafile : string path to text file of user agents, one per line
    """
    UAs = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                UAs.append(ua.strip()[1:-1 - 1])
    random.shuffle(UAs)
    return UAs


ua_list = LoadUserAgents('user_agents.txt')
queueLock = threading.Lock()


def get_source(ua_list, page_nums):
    global page_num
    print("page_num: {0}".format(page_num))
    
    if page_num < page_nums:

        time.sleep(2)
        User_Agent = random.choice(ua_list)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'sid=hwyca77b; UM_distinctid=1618f310ef48ee-06f640e0266aee-d35346d-100200-1618f310ef5662; '
                      'buvid3=4E00C1AE-4808-4971-BA81-2543A839DC1D12200infoc; fts=1518525814; pgv_pvi=6756619264; '
                      'pgv_si=s9232883712; rpdid=kwqpqopipldosoqsislww; finger=edc6ecda; DedeUserID=82217945; '
                      'DedeUserID__ckMd5=758c3b0fc8c3615f; SESSDATA=c5b279bc%2C1524458944%2C1107dbe2; '
                      'bili_jct=ece27f788664bb3dd3eee10e76ea61ec; CURRENT_QUALITY=64; '
                      '_dfcaptcha=36b9499a019e71ee34eabbcbc9192274; LIVE_BUVID=72dd9d89034586b7f662f014785af9bc; '
                      'LIVE_BUVID__ckMd5=dc89bf9db942a636',
            'Host': 'api.bilibili.com',
            'Referer': 'https://www.bilibili.com/v/douga/mad/?spm_id_from=333.5.douga_mad.3',
            'User-Agent': User_Agent,
        }

        payload = {'callback': 'jqueryCallback_bili_6', 'rid': '24', 'type': '0', 'pn': str(page_num), 'ps': '20',
                   'jsonp': 'jsonp', '_': '1523784493329'}
        url = 'https://api.bilibili.com/x/web-interface/newlist?'
        start_html = requests.get(url, headers=headers, params=payload)
        print("******** Linking...: {0} page {1}*******".format(page_num, start_html.url))
        global get_source_flag
        if start_html.status_code == requests.codes.ok:
            pattern = re.compile(r'.*?"pic":"(.*?)".*?', re.S)
            items = re.findall(pattern, start_html.text)
            if items:
                for i in range(len(items)):
                    if items[i] not in Img_Url:
                        # print("Image_Link: {0}".format(items[i]))
                        Img_Url.append(items[i])
            Image_url_num = len(Img_Url)
            get_source_flag = 1

        else:
            print("Error: {0}".format(start_html.raise_for_status))
            get_source_flag = 0
        page_num += 1

    # return get_source_flag


def Save_Image(Image_url):
    global name  # UnboundLocalError: local variable 'name' referenced before assignment
    while Image_url:
        name = name + 1
        with open('./image/' + str(name) + '.jpg', 'wb') as fd:
            img = requests.get(Image_url.pop()).content
            time.sleep(random.choice(range(1, 3)) / 10)
            fd.write(img)
            fd.close()
    # return 0


class myThread(threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        # print(type(self.name))
        if self.name == 'get_source':
            
            # print("open processing:" + self.name)
            get_source_thread(self.name)
            # print("close processing:" + self.name)
        else:
            queueLock.acquire()
            # print("open processing:" + self.name)
            Save_Image_thread(self.name)
            # print("close processing:" + self.name)


def get_source_thread(threadName=get_source):
    """
    :description: get_source_thread
    :param threadName:
    """
    global page_all_num
    queueLock.acquire()
    if Image_url_num:
        get_source(ua_list=ua_list, page_nums=page_all_num)
        # print("len(Img_Url){0}".format(len(Img_Url)))
        queueLock.release()
        print("%s processing" % (threadName))
    else:
        queueLock.release()


def Save_Image_thread(threadName=Save_Image):
    """
    :description: get_source_thread
    :param threadName:
    """
    if Image_url_num:
        Save_Image(Img_Url)
        print("Save_Image...")
        queueLock.release()
        print("%s processing" % (threadName))
    else:
        queueLock.release()


if __name__ == '__main__':
	
    # global page_all_num
    threadnames = ['get_source', 'Save_Image']
    thread_list = []
    thread_num = 1

    thread = myThread(0, 'get_source')
    thread.start()
    thread.join()
    while Img_Url or page_num < page_all_num:
        for threadname in threadnames:
            print(threadname)
            thread = myThread(thread_num, str(threadname))
            thread.start()
            thread_list.append(thread)
            thread_num += 1

        for t in thread_list:
            t.join()
    print("All Thread Number:{0}".format(thread_num))
    print("close the main processing")
