#coding=UTF-8
import urllib
import urllib2
import json
from bs4 import BeautifulSoup
import time
import random
import os
import config
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
ips = []
url = 'http://club.jd.com/review/' #%s-0-%d-0.html'
url_suffix = '-0-%d-0.html'
json_url = 'http://item.m.jd.com/ware/comments.json?wareId='
web_json_url = 'http://club.jd.com/productpage/p-%s-s-0-t-3-p-%d.html'
mobile_suffix = '&score=%d&sid=%s&page=%d'
#suffix = '&score=%d&page=%d'
headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

user_proxy = False

#headers = {'Host': 'club.jd.com','Referer': 'http://item.jd.com/0.html'}
def get_page_num(url):
    page_url = url % 0
    req = urllib2.Request(url = page_url, headers = headers)
    page = urllib2.urlopen(req).read().decode('gb18030')
    soup_page = BeautifulSoup(page)
    page_nums = soup_page.find('div', class_ = 'pagin').find_all('a')
    #print page_nums
    return int(page_nums[-2].string)
    #print page_nums[-2].string.encode('utf-8')

def scraw_comments(url, file_name):

    page_num = get_page_num(url)
    #page_num = 5
    fp  = open(file_name, 'w')
    comment_set = set()
    i = 1
    while i < page_num + 1:
    #for i in range(1, page_num + 1):
        sec = random.randint(2,4)
        #time.sleep(sec)
        page_url = url % i
        ip = random.choice(ips)
        ip_address = 'http://%s' % ip
        print ip_address
        proxy_handler = urllib2.ProxyHandler({"http":ip_address})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
        req = urllib2.Request(url = page_url, headers = headers)

        try:
            page = urllib2.urlopen(req).read().decode('gb18030')
        except Exception, e:
            print i, e
            break
        #print page.encode('utf-8')
        soup_page = BeautifulSoup(page)
        #print soup_page.prettify().encode('utf-8')
        if i == 1:
            p_info = soup_page.find('li', class_ = "p-name")
            p_name_tag = p_info.find('a', target = "_blank")
            p_name =  p_name_tag.string.encode('utf-8')
            fp.write(p_name + '\n')

        comment_list = soup_page.find('div',id = 'comments-list')
        comments= comment_list.find_all('div', class_= 'mc')
        count = 1
        fp.write('page %d:%s\n' % (i, page_url, ))

        for j, comment in enumerate(comments):
            try:
                comment_content = comment.find('div', class_ = 'comment-content')
                dls = comment_content.find_all('dl')
                #username = comment.find('div', class_ = 'u-name').string.encode('utf-8')
                #fp.write(username +':')
                for dl in dls:
                    #print dl.find('dt').string.encode('utf-8')
                    if dl.find('dt').string == u'心　　得：':
                        dd = dl.find('dd').string
                        if dd in comment_set:
                            continue
                        comment_set.add(dd)
                        print 'len of set:', len(comment_set)
                        fp.write(dd.encode('utf-8') + '\n')
                        #print count
                        count += 1
            except Exception, e:
                print e
                break
        i += 1
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
    return page_dict['productCommentSummary']['commentCount']

def get_comments(pid, page_num):
    headers1 = {'GET': '',
    'Host': "club.jd.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 6.2; rv:29.0) Gecko/20100101 Firefox/29.0",
    'Referer': 'http://item.jd.com/%s.html' % (pid)}
    page_url = web_json_url % (pid, page_num)
    req = urllib2.Request(url = page_url, headers = headers1)
    contents = []
    for i in range(20):
        if user_proxy:
            ip = random.choice(ips)
            ip_address = 'http://%s' % ip
            print ip_address
            proxy_handler = urllib2.ProxyHandler({"http":ip_address})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)
        try:
            page_data = urllib2.urlopen(req).read()
            page_dict = json.loads(page_data.decode('gbk'))
            comments = page_dict['comments']
        except Exception, e:
            print e
            continue
        for comment in comments:
            contents.append(comment['content'])

    return contents

#def read_failed(url, file_name, score, failed_page_nums):


def scraw_web_json(pid, file_name):
    max_page_num = get_max_page_num(pid)
    print max_page_num /10 + 1
    page_num = 1
    content_set = set()
    fp = open(file_name, 'w')
    que = range(1, max_page_num + 1)
    while len(que) > 10:
        page_num = que.pop(0)
        contents = get_comments(pid, page_num)
        print 'page_num:',page_num
        if len(contents) == 0 :
            print 'empty'
            que.append(page_num)
            continue
        for content in contents:
            if content in content_set:
                continue
            content_set.add(content)
            print len(content_set)
            fp.write(content.encode('utf-8') + '\n')


def save_failed_page(save_dir, pid, failed_pages):
    file_name = os.path.join(save_dir, 'failed_page')
    fp = open(file_name, 'w')
    for failed_page in failed_pages:
        fp.write(' '.join([pid, failed_page[0], failed_page[1], ]) + '\n')

    fp.close()


def read_failed_page(save_dir):
    failed_pages_file = os.path.join(save_dir, 'failed_page')
    fp = open(failed_pages_file, 'r')
    page_dict = {}
    for line in fp.readlines():
        tokens = line.strip().split(' ')
        pid = tokens[0]
        score = tokens[1]
        page = tokens[2]
        page_dict.setdefault(pid, []).append((score, page))

    for pid in page_dict.keys():
        cur_url = ''.join((json_url , pid , mobile_suffix))
        file_name = os.path.join(save_dir, pid)
        fp2 = open(file_name, 'a')
        que = page_dict[pid]
        failed_pages = get_mobile_comments(que, cur_url, fp2)
        save_failed_page(save_dir, pid, failed_pages)




def scraw_mobile_wap(phone_id, file_name):
    cur_url = ''.join((json_url , phone_id , mobile_suffix))
    fp = open(file_name, 'w')
    start_url = cur_url %(1, '', 1)
    req = urllib2.Request(url = start_url, headers = headers)
    page_data = urllib2.urlopen(req).read()
    page_dict = json.loads(page_data)
    sid =  page_dict['sid']
    scoreCount3 = page_dict['commentCountMap']['scoreCount3']
    scoreCount2 = page_dict['commentCountMap']['scoreCount2']
    scoreCount1 = page_dict['commentCountMap']['scoreCount1']
    total_count = scoreCount1 + scoreCount2 + scoreCount3
    que = []
    for score in range(1, 6):
        page_num = 1
        total_page_num = 0
        if score == 1:
            total_page_num = int(scoreCount3) / 15 + 1
        elif score == 2 or score == 3:
            total_page_num = int(scoreCount2) / 15 + 1
        elif score == 4 or score == 5:
            total_page_num = int(scoreCount1) / 15 + 1
        for page_num in range(1, total_page_num + 1):
            que.append((score, page_num))

    failed_page = get_mobile_comments(que, cur_url, fp)

    return failed_page


def get_mobile_comments(que, cur_url, fp):
    comment_set = set()
    page_count_dict = {}
    start_url = cur_url %(1, '', 1)
    resp = urllib2.Request(url = start_url, headers = headers)
    page_data = urllib2.urlopen(resp).read()
    page_dict = json.loads(page_data)
    sid =  page_dict['sid']
    while len(que) != 0:
        ele = random.choice(que)
        que.remove(ele)
        score = ele[0]
        page_num = ele[1]
        print 'score %d, page %d:' %(score, page_num)
        page_url = cur_url % (score, sid, page_num)
        #print page_url
        sec = random.randint(1,2)
        #time.sleep(sec)
        req = urllib2.Request(url = page_url, headers = headers)
        if user_proxy:
            ip = random.choice(ips)
            ip_address = 'http://%s' % ip
            print ip_address
            proxy_handler = urllib2.ProxyHandler({"http":ip_address})
            opener = urllib2.build_opener(proxy_handler)
            urllib2.install_opener(opener)

        try:
            f = urllib2.urlopen(req, timeout = 10)
            page = f.read()#.decode('gb18030')
            code = f.getcode()
            print page_url, code
            dicts = json.loads(page)
        except Exception, e:
            print e
            page_count_dict[ele] = page_count_dict.setdefault(ele, 0) + 1
            if page_count_dict[ele] >= 20:
                failed_page.append(ele)
                continue
            que.append(ele)
            continue
        if 'comments' not in dicts.keys() or len(dicts['comments']) == 0:
            print 'empty'
            page_count_dict[ele] = page_count_dict.setdefault(ele, 0) + 1
            if page_count_dict[ele] >= 20:
                failed_page.append(ele)
                continue
            que.append((score, page_num))


        for comment in dicts['comments']:
            content = comment['content']
            if content in comment_set:
                print 'duplicate:', len(comment_set)
                continue
            comment_set.add(content)
            print len(comment_set)
            fp.write(content.encode('utf-8') + '\n')
             
    return failed_page
    fp.close()


    

def read_proxy(file_name):
    fp = open(file_name)
    ips = []
    for line in fp:
        ip = line.strip()
        ips.append(ip)
    return ips


if __name__ == '__main__':

    phone_id_dict = config.phones
    

    ips = read_proxy('proxy300.txt')

    #save_dir = 'smartisian'
    save_dir = 'xiaomi'
    #for chuizi_id in chuizi_ids:
    phone_ids = ['1743187']
    #phone_ids = phone_id_dict['lianxiang']
    for phone_id in phone_ids:
        #cur_url = url + phone_id + url_suffix
        

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        file_name = os.path.join(save_dir, phone_id)
        print 'phone_id:',phone_id
        #scraw_web_json(phone_id, file_name)
        failed_pages = scraw_mobile_wap(phone_id, file_name)
        save_failed_page(save_dir, failed_pages)
        #selenium_scraw(cur_url, file_name)
        #scraw_comments(cur_url, file_name)
    
