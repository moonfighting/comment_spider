#coding=UTF-8
import urllib
import urllib2
import json
from bs4 import BeautifulSoup
import time
import random
import os
import re
import threading
import Queue
import cookielib
import config
headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

#base_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=521893618096&sellerId=263726286&currentPage=%d'
base_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&sellerId=%s&currentPage=%d'

huawei = 'https://huawei.tmall.com/category-1022967656.htm'
def get_Tmall_comment(itemId, sellerId, save_dir):
    if not os.path.exists(save_dir):
            os.mkdir(save_dir)
    file_name = os.path.join(save_dir, sellerId + '_' + itemId)
    fp = open(file_name, 'w')
    comment_set = set()
    for i in range(1, 100):
        page_url = base_url % (itemId, sellerId, i)
        req = urllib2.Request(url = page_url, headers = headers)
        try:
            page_data = urllib2.urlopen(req).read().decode('gbk')
        except Exception, e:
            print 'page:',i,e
            continue
        try:
            myjson = re.findall('\"rateList\":(\[.*?\])\,\"tags\"',page_data)[0]
            page_dict = json.loads(myjson)
        except Exception, e:
            print 'page:',i,e
            continue
        if len(page_dict) == 0:
            break
        for comment_info in page_dict:
            comment = comment_info['rateContent']
            if comment in comment_set:
                continue
            comment_set.add(comment)
            fp.write(comment.encode('utf-8')+'\n')
    fp.close()
    print len(comment_set)


def get_huawei_phone_list(url):
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    resp = opener.open(url)
    page = resp.read().decode('gbk')
    print page.encode('utf-8')


if __name__ == '__main__':
    phone_ids = config.phone_ids

    for brand in phone_ids.keys():
        shops = phone_ids[brand]
        for seller in shops.keys():
            pids = shops[seller]
            for pid in pids:
                print brand, seller, pid
                get_Tmall_comment(pid, seller, brand)

    