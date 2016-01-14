#coding=UTF-8
import urllib
import urllib2
import json
import time
import random
import os
import re

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

#base_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=521893618096&sellerId=263726286&currentPage=%d'
base_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&sellerId=%s&currentPage=%d'

def get_Tmall_comment(itemId, sellerId, save_dir): #itemId 是商品的id, sellerId是卖家的id
    if not os.path.exists(save_dir):
            os.mkdir(save_dir)
    file_name = os.path.join(save_dir, sellerId + '_' + itemId) 
    fp = open(file_name, 'w')
    comment_set = set()
    for i in range(1, 100): # 最多只能爬取99页评论
        page_url = base_url % (itemId, sellerId, i)
        req = urllib2.Request(url = page_url, headers = headers)
        try:
            page_data = urllib2.urlopen(req).read().decode('gbk')
        except Exception, e:
            print 'page:',i,e
            continue
        try:
            myjson = re.findall('\"rateList\":(\[.*?\])\,\"tags\"',page_data)[0]  #从json数据中匹配评论的部分
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


if __name__ == '__main__':
    item_id = '521875831541'
    seller_id = '1917047079'
    save_dir = '.';
   
    get_Tmall_comment(item_id, seller_id, save_dir)

    
