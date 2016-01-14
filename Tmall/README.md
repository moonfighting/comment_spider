## 天猫评论爬虫脚本
该脚本可以用来爬取天猫上的商品的评论.

天猫商品的评论的原始url是：

https://rate.tmall.com/list_detail_rate.htm?itemId=1917047079&sellerId=521875831541&currentPage=1

其中itemId表示商品的id, sellerId表示店铺的id, currentPage表示第几页的评论。

天猫对于评论数据爬虫的限制是只能爬取前99页的评论，这一点需要注意。

函数 `get_one_page_comment(item_id, seller_id, page_num)` 根据给定的item_id,seller_id和page_num以列表的形式返回商品某一页的评论，然后可以进行后续的处理

