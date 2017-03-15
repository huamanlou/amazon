# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
import json
import time


#mysql数据库方法
class HtmlDeal:
    doc = ''
    selector = ''

    def __init__(self, response):
        self.doc = pq(response.body)
        self.selector = response.selector



    # 判断是否是图书，假如是图书的话，则放弃
    def isbook(self):
        # bsr = selector.xpath('//*[@id="SalesRank"]/ul//text()').extract()
        bsr = self.doc('#SalesRank ul').text()
        # 不同dom，这里结构不一样，玩具类别用下面
        if len(bsr) < 1:
            # bsr = doc('#productDetails_detailBullets_sections1 tr').eq(8).find('td').text()
            bsr_td = self.doc('#productDetails_detailBullets_sections1 td')
            for td in bsr_td.items():
                td_text = td.text()
                if td_text.find(' > ') != -1:
                    bsr = td_text
                    break

        isbook = 0
        if bsr.find('Books') != -1 or bsr.find('Video Games') != -1:
            isbook = 1

        res = {'bsr': bsr, 'isbook': isbook}
        return res

    def get_products(self):
        # 页面抓取相关产品json数据包
        sim_feature = self.selector.css('div[id="purchase-sims-feature"]')
        if len(sim_feature) > 0:
            customer_product = sim_feature.css('div::attr(data-a-carousel-options)').extract_first()
        else:
            customer_product = self.doc('#session-sims-feature .p13n-sc-carousel').attr('data-a-carousel-options')
        print(customer_product)
        customer_product_list = []
        if customer_product:
            customer_product = json.loads(customer_product)
            customer_product_list = customer_product['ajax']['id_list']

        # 页面抓取广告产品json数据包
        sponsored_product = self.doc('#sponsored-products-dp_feature_div #sp_detail').attr('data-a-carousel-options')
        sponsored_product_list = []
        if sponsored_product:
            sponsored_product = json.loads(sponsored_product)
            sponsored_product_list = sponsored_product['initialSeenAsins'].split(',')

        res = {'customer_product_list': customer_product_list, 'sponsored_product_list': sponsored_product_list}
        return res

    def get_items(self):
        # 开始处理页面信息，写入本地文件
        res = {}
        # 标题
        title = self.selector.css('span[id="productTitle"]::text').extract_first()
        if title:
            res['title'] = title.strip()

        # 品牌名称
        brand = self.selector.css('a[id="brand"]::text').extract_first()
        if brand:
            brand = brand.strip()
        res['brand'] = brand
        # 卖点
        res['bullet_point'] = ''
        bullet_point = self.selector.css('div[id="feature-bullets"] .a-list-item::text').extract()
        if bullet_point:
            for point in bullet_point:
                res['bullet_point'] = res['bullet_point'] + point.strip() + '\n '
        # 页面结构不一样
        else:
            point_li = self.doc('#feature-bullets-btf li')
            for point in point_li.items():
                res['bullet_point'] = res['bullet_point'] + point.text() + '\n '

        # 是否亚马逊发货
        res['isPrime'] = ''
        # 销量
        res['sales'] = ''
        # 库存
        stock = self.selector.css('select[id="quantity"] option:last-child::text').extract_first()
        if stock:
            res['stock'] = stock.strip()
        # 评价得分，星级
        stars = self.selector.css('.a-declarative .a-icon-alt::text').extract_first()
        if stars:
            stars = stars[:stars.index(' ')]
        res['stars'] = stars
        # 评价总数
        reviews = self.selector.css('span[id="acrCustomerReviewText"]::text').extract_first()
        if reviews:
            reviews = reviews[:reviews.index(' ')]
        res['reviews'] = reviews
        # 问题总数
        questions = self.selector.css('a[id="askATFLink"] .a-size-base::text').extract_first()
        if questions:
            questions = questions.strip()
            questions = questions[:questions.index(' ')]
        res['questions'] = questions
        # 商品销售价格
        res['price'] = self.selector.css('span[id="priceblock_ourprice"]::text').extract_first()
        # 跟卖数量
        res['to_sell'] = ''
        res['ctime'] = time.strftime('%Y%m%d', time.localtime(time.time()))

        return res