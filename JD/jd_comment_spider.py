#coding=UTF-8
import urllib
import urllib2
import json
import time
import random
import os
import threading
from bs4 import BeautifulSoup

user_proxy = True
ips = []
web_json_url = 'http://club.jd.com/productpage/p-%s-s-0-t-3-p-%d.html'  #京东商品评论的json页面，第一个%s参数为商品id，第二个%d参数为评论的页数
comments = set()

class CommentDownload(threading.Thread):         #利用多线程爬取，一般用不到
    def __init__(self,queue, pid, file_name):
        threading.Thread.__init__(self)
        self.queue = queue
        self.file_name = file_name
        self.pid = pid
        #self.setDaemon(True)

    def run(self):
        global comments
        while True:
            fp = open(file_name, 'a')    
            page_num = self.queue.get()
            print 'page num:', page_num
            sec = random.randint(1,4)
            time.sleep(sec)
            contents = get_comments(pid, page_num)
            if len(contents) == 0:
                self.queue.put(page_num)
                continue
            for content in contents:
                if content in comments:
                    continue
                print len(comments)
                fp.write(content.encode('utf-8') + '\n')
            comments.update(contents)
            print 'comments number:', len(comments)
            if self.queue.empty():
                print 'queue empty'
                break
            self.queue.task_done()
            fp.close()

def get_max_page_num(pid):
    page_url = web_json_url % (pid, 0)
    headers1 = {'GET': '',
    'Host': "club.jd.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; rv:29.0) Gecko/20100101 Firefox/29.0",
    'Referer': 'http://item.jd.com/%s.html' % (pid)}
    req = urllib2.Request(url = page_url, headers = headers1)
    page_data = urllib2.urlopen(req).read().decode('gbk', 'ignore')
    page_dict = json.loads(page_data)
    return page_dict['productCommentSummary']['commentCount'] / 10 + 1

def get_comments(pid, page_num):   #爬取商品id为pid的商品的第page_num页的评论
    headers1 = {'GET': '',
    'Host': "club.jd.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; rv:29.0) Gecko/20100101 Firefox/29.0",
    'Referer': 'http://item.jd.com/%s.html' % (pid)}
    page_url = web_json_url % (pid, page_num)
    req = urllib2.Request(url = page_url, headers = headers1)
    contents = []
    try:
        page_data = urllib2.urlopen(req, timeout = 10).read()
        page_dict = json.loads(page_data.decode('gbk', 'ignore'))
        comments = page_dict['comments']
    except Exception, e:
        print e
        return []
    try:
        for comment in comments:
            contents.append(comment['content'])
    except Exception, e:
        print e
        return []
    return contents

def scraw_web_json(pid, file_name):
    max_page_num = get_max_page_num(pid)
    print max_page_num
    content_set = set()
    fp = open(file_name, 'w')

    for page_num in range(max_page_num):
        print 'page_num:',page_num
        #time.sleep(random.randint(1,2))
        contents = get_comments(pid, page_num)
        if len(contents) == 0:                #京东对商品评论的爬取有限制，只能抓取到最近一个月内的商品评论，再之前的评论都抓不到
            print 'done'
            return
        for content in contents:
            if content in content_set:
                continue
            content_set.add(content)         #用一个集合来进行去重
            print content.encode('utf-8')
            fp.write(content.encode('utf-8') + '\n')



if __name__ == '__main__':


    #save_dir = 'smartisian'
    save_dir = 'xiaomi'
    #for chuizi_id in chuizi_ids:
    phone_ids = ['1743191']
    for pid in phone_ids:
        print 'phone_id:',pid
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        file_name = os.path.join(save_dir, pid + '.txt')
        scraw_web_json(pid, file_name)

