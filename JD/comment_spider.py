#coding=UTF-8
import urllib
import urllib2
import json
from bs4 import BeautifulSoup
import time
import random
import os
import config
import threading
import Queue

user_proxy = True
ips = []
web_json_url = 'http://club.jd.com/productpage/p-%s-s-0-t-3-p-%d.html'
comments = set()

class CommentDownload(threading.Thread):
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

def get_comments(pid, page_num):
    headers1 = {'GET': '',
    'Host': "club.jd.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; rv:29.0) Gecko/20100101 Firefox/29.0",
    'Referer': 'http://item.jd.com/%s.html' % (pid)}
    page_url = web_json_url % (pid, page_num)
    req = urllib2.Request(url = page_url, headers = headers1)
    contents = []
    for i in range(1):
        comments = []
        if user_proxy:
            ip = random.choice(ips)
            ip_address = 'http://%s' % ip
            print ip_address
            proxy_handler = urllib2.ProxyHandler({"http":ip_address})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        try:
            page_data = urllib2.urlopen(req, timeout = 10).read()
            page_dict = json.loads(page_data.decode('gbk'))
            comments = page_dict['comments']
        except Exception, e:
            print e
            continue
        try:
            for comment in comments:
                contents.append(comment['content'])
        except Exception, e:
            print e
            continue
        if len(contents) != 0:
            break
    return contents

#def read_failed(url, file_name, score, failed_page_nums):


def scraw_web_json(pid, file_name):
    max_page_num = get_max_page_num(pid) / 10 + 1
    print max_page_num
    page_num = 1
    content_set = set()
    fp = open(file_name, 'w')
    que = range(1, max_page_num + 1)
    failed_pages = []
    while len(que) != 0:
        page_num = que.pop(0)
        print 'page_num:',page_num
        sec = random.randint(1,2)
        time.sleep(sec)
        contents = get_comments(pid, page_num)
        if len(contents) == 0:
            print 'empty'
            failed_pages.append(page_num)
            continue
        for content in contents:
            if content in content_set:
                continue
            content_set.add(content)
            print len(content_set)
            fp.write(content.encode('utf-8') + '\n')

    return failed_pages



def save_failed_page(save_dir, pid, failed_pages):
    file_name = os.path.join(save_dir, pid + '_failed_page')
    fp = open(file_name, 'w')
    for failed_page in failed_pages:
        fp.write(' '.join([pid, failed_page]) + '\n')

    fp.close()


def read_failed_page(save_dir, pid):
    failed_pages_file = os.path.join(save_dir, pid + '_failed_page')
    fp = open(failed_pages_file, 'r')
    content_set = set()
    failed_pages  = []
    for line in fp.readlines():
        tokens = line.strip().split(' ')
        pid = tokens[0]
        page = tokens[1]
        contents = get_comments(pid, page)
        file_name = os.path.join(save_dir, pid)
        fout = open(file_name, 'a')
        if len(contents) == 0 :
            print 'empty'
            failed_pages.append(page_num)
            continue
        for content in contents:
            if content in content_set:
                continue
            content_set.add(content)
            print len(content_set)
            fout.write(content.encode('utf-8') + '\n')
    return failed_pages

def read_proxy(file_name):
    fp = open(file_name)
    ips = []
    for line in fp:
        ip = line.strip()
        ips.append(ip)
    return ips


def get_queue(max_page_num):
    queue = Queue.Queue()
    for i in range(1, max_page_num + 1):
        queue.put(i)
    return queue


if __name__ == '__main__':

    phone_id_dict = config.phones
    

    ips = read_proxy('proxy200.txt')

    #save_dir = 'smartisian'
    save_dir = 'xiaomi'
    #for chuizi_id in chuizi_ids:
    phone_ids = ['1743191']
    #phone_ids = phone_id_dict['lianxiang']
    for pid in phone_ids:
        print 'phone_id:',pid

        max_page_num = get_max_page_num(pid)
        queue = get_queue(max_page_num)
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        file_name = os.path.join(save_dir, pid)
        threads = []
        for i in range(0,10):
            t = CommentDownload(queue, pid, file_name)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        print "Exiting Main Thread"

        #scraw_web_json(phone_id, file_name)
        #failed_pages = scraw_web_json(phone_id, file_name)
        #save_failed_page(save_dir, failed_pages)
    

    #print 'first time end'

    #for phone_id in phone_ids:
    #    failed_pages = read_failed_page(save_dir, phone_id)
    #    if len(failed_pages) == 0:
    #        continue
    #    save_failed_page(save_dir, phone_id, failed_pages)

