#coding=UTF-8
import urllib
import urllib2
import json
import time
import random
import os
import re

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}

base_url = 'https://rate.tmall.com/list_detail_rate.htm?itemId=%s&sellerId=%s&currentPage=%d' #评论页面的url（Json数据) 

def get_Tmall_comment(itemId, sellerId, save_dir): #itemId 是商品的id, sellerId是卖家的id
    if not os.path.exists(save_dir):
            os.mkdir(save_dir)
    file_name = os.path.join(save_dir, sellerId + '_' + itemId) #以seller_id + item_id作为文件名保存评论内容 
    fp = open(file_name, 'w')
    comment_set = set()
    for page_num in range(1, 10): # 最多只能爬取99页评论
        comments = get_one_page_comment(item_id, seller_id, page_num)    
        for comment in comments:
            fp.write(comment.encode('utf-8')+'\n')
    fp.close()


def get_one_page_comment(item_id, seller_id, page_num):  #根据item_id，和seller_id获取某一页的评论
    page_url = base_url % (item_id, seller_id, page_num)
    req = urllib2.Request(url = page_url, headers = headers)
    try:
        page_data = urllib2.urlopen(req).read().decode('gbk')
    except Exception, e:
        print 'page:',page ,e
        return []
    try:
        myjson = re.findall('\"rateList\":(\[.*?\])\,\"tags\"',page_data)[0]  #从json数据中匹配评论的部分
        page_dict = json.loads(myjson)  
    except Exception, e:
        print 'page:',i,e
        return []
    if len(page_dict) == 0:
        return []
    comments = []
    for comment_info in page_dict:
        comment = comment_info['rateContent']
        comments.append(comment)

    return comments



if __name__ == '__main__':
    item_id = '521875831541'
    seller_id = '1917047079'
    save_dir = '.';
   
    get_Tmall_comment(item_id, seller_id, save_dir)

    
