# -*- coding: utf-8 -*-
import MySQLdb
import scrapy
import time
import json
from pyquery import PyQuery as pq
from amazon.items import AmazonItem



#mysql数据库方法
class MysqlDo:
    host = '104.128.85.252'
    user = 'amazon'
    passwd = 'Amazon123!@#'
    # user = 'root'
    # passwd = 'fuck2013'
    db = 'amazon_us'
    charset = 'utf8'
    conn = ''
    def __init__(self):
        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)

    def close_conn(self):
        self.conn.close()
    #查找索引表
    def select_asin(self, asin):
        cursor = self.conn.cursor()
        cursor.execute("select * from t_asin where asin= '%s'" % (asin))
        row = cursor.fetchall()
        # self.conn.close()
        return len(row)
    #插入索引表
    def insert_asin(self, asin):
        cursor = self.conn.cursor()
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = "insert into t_asin(asin,ctime, status) value ('%s', '%s', '%d')"
        cursor.execute(sql % (asin,ctime,1))
        self.conn.commit()

    #标志索引表商品是亚马逊自营书籍
    def update_asin_isbook(self, asin):
        cursor = self.conn.cursor()
        # 更新状态
        sql = "update t_asin set isbook = 1 where asin = '%s'" % (asin)
        # 执行SQL语句
        cursor.execute(sql)
        self.conn.commit()

    #查找爬虫任务表
    def select_scrapy(self, num):
        cursor = self.conn.cursor()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        cursor.execute("select asin from t_scrapy where status=0 and date='%s' limit %d" % (date,num))
        asin_rows = cursor.fetchall()
        #这里有个坑，取出来是双层tuple,但是mysql可以执行，下面无法直接取值
        print(asin_rows)
        if len(asin_rows) == 0:
            return 0

        #todo -- 更新状态,拼接in 语句没成功，先循环处理,
        # asin_list = ','.join(['%s'] * len(row))
        # sql = "update t_scrapy set status = 1 where asin in (%s)" % (asin_list)
        # # 执行SQL语句
        # cursor.execute(sql, row)
        # # 提交到数据库执行
        # self.conn.commit()

        for asin in asin_rows:
            sql = "update t_scrapy set status = 1 where asin = '%s' and date='%s'" % (asin[0],date)
            # 执行SQL语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()


        return asin_rows

    #更新爬虫任务标志位
    def update_scrapy(self, asin):
        cursor = self.conn.cursor()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        #更新状态
        sql = "update t_scrapy set status = 2 where asin = '%s' and date='%s'" % (asin,date)
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        self.conn.commit()



#爬虫规则
class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com/dp/'
    # start_urls = ['https://www.amazon.com/dp/B01BLQ24IW','https://www.amazon.com/dp/B01N3092ZS?psc=1']
    start_urls = []

    def __init__(self):
        #从db取出一个asin进行爬取
        mysql_do = MysqlDo()
        asin_rows = mysql_do.select_scrapy(1)
        for asin in asin_rows:
            print(asin[0])
            init_url = self.base_url + asin[0]
            self.start_urls.append(init_url)

    def parse(self, response):
        item = AmazonItem()
        mysql_do = MysqlDo()
        doc = pq(response.body)
        selector = response.selector
        # asin
        #asin = selector.css('input[id="ASIN"]::attr(value)').extract_first()
        url = response.url
        asin = url[url.rfind('/')+1:len(url)]

        #判断是否是图书，假如是图书的话，则放弃
        # bsr = selector.xpath('//*[@id="SalesRank"]/ul//text()').extract()
        bsr = doc('#SalesRank ul').text()
        #不同dom，这里结构不一样，玩具类别用下面
        if len(bsr)<1:
            bsr = doc('#productDetails_detailBullets_sections1 tr').eq(8).find('td').text()
        isbook = 0
        if bsr.find('Books') != -1:
            isbook = 1

        print('is book')
        print (isbook)
        #假如是图书，索引表作标志，并且退出，不做数据处理
        if isbook==1:
            #更新索引表标志
            mysql_do.update_asin_isbook(asin)
            # 修改状态
            mysql_do.update_scrapy(asin)
            # 继续塞进程爬
            next_asins = mysql_do.select_scrapy(1)
            if next_asins == 0:
                return
            for asin in next_asins:
                product_url = self.base_url + asin[0]
                print(product_url)
                yield scrapy.Request(product_url, callback=self.parse)

            return

        # 页面抓取相关产品json数据包
        sim_feature = selector.css('div[id="purchase-sims-feature"]')
        if len(sim_feature)>0:
            products_data = sim_feature.css('div::attr(data-a-carousel-options)').extract_first()
        else:
            products_data = doc('#session-sims-feature .p13n-sc-carousel').attr('data-a-carousel-options')
        print(products_data)
        if products_data:
            products_data = json.loads(products_data)
            asin_list = products_data['ajax']['id_list']
            # 循环读取asin，查询数据库，若不存在，则插入数据库
            for asin_key in asin_list:
                row = mysql_do.select_asin(asin_key)
                if row < 1:
                    mysql_do.insert_asin(asin_key)

        #开始处理页面信息，写入本地文件

        # 标题
        title = selector.css('span[id="productTitle"]::text').extract_first()
        if title:
            item['title'] = title.strip()

        item['asin'] = asin
        # 品牌名称
        brand = selector.css('a[id="brand"]::text').extract_first()
        if brand:
            brand = brand.strip()
        item['brand'] = brand
        # 卖点
        item['bullet_point'] = ''
        bullet_point = selector.css('div[id="feature-bullets"] .a-list-item::text').extract()
        if bullet_point:
            for point in bullet_point:
                item['bullet_point'] = item['bullet_point'] + point.strip() + '\n '
        #页面结构不一样
        else:
            point_li = doc('#feature-bullets-btf li')
            for point in point_li.items():
                item['bullet_point'] = item['bullet_point'] + point.text() + '\n '

        # 是否亚马逊发货
        item['isPrime'] = ''
        # 销量
        item['sales'] = ''
        # 分类排名
        item['bsr'] = bsr
        # 库存
        stock = selector.css('select[id="quantity"] option:last-child::text').extract_first()
        if stock:
            item['stock'] = stock.strip()
        # 评价得分，星级
        stars = selector.css('.a-declarative .a-icon-alt::text').extract_first()
        if stars:
            stars = stars[:stars.index(' ')]
        item['stars'] = stars
        # 评价总数
        reviews = selector.css('span[id="acrCustomerReviewText"]::text').extract_first()
        if reviews:
            reviews = reviews[:reviews.index(' ')]
        item['reviews'] = reviews
        # 问题总数
        questions = selector.css('a[id="askATFLink"] .a-size-base::text').extract_first()
        if questions:
            questions = questions.strip()
            questions = questions[:questions.index(' ')]
        item['questions'] = questions
        # 商品销售价格
        item['price'] = selector.css('span[id="priceblock_ourprice"]::text').extract_first()
        # 跟卖数量
        item['to_sell'] = ''
        item['ctime'] = time.strftime('%Y%m%d', time.localtime(time.time()))
        print(item)
        yield item

        #修改状态
        mysql_do.update_scrapy(asin)

        #继续塞进程爬
        next_asins = mysql_do.select_scrapy(2)
        if next_asins == 0:
            return
        for asin in next_asins:
            product_url = self.base_url + asin[0]
            print(product_url)
            yield scrapy.Request(product_url, callback=self.parse)

        #mysql_do.close_conn()


'''
class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com/dp/'
    start_urls = [
        'https://www.amazon.com/dp/B01KLSMWVA/'
    ]

    def parse(self, response):
        selector = response.selector
        #页面抓取相关产品json数据包
        sim_feature = selector.css('div[id="purchase-sims-feature"]')
        products_data = sim_feature.css('div::attr(data-a-carousel-options)').extract_first()
        products_data = json.loads(products_data)
        asin_list = products_data['ajax']['id_list']
        #循环读取asin，查询数据库，若不存在，则插入数据库
        mysql_do = MysqlDo()
        for asin in asin_list:
            row = mysql_do.select_asin(asin)
            if row<1:
                mysql_do.insert_asin (asin)
                #入库后，将新的asin，重新开启爬虫进程
                product_url = self.base_url + asin
                yield scrapy.Request(product_url, callback=self.parse)


        mysql_do.close_conn()


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    start_urls = [
        'https://www.amazon.com/gp/product/B01BLQ24IW/'
        'https://www.amazon.com/dp/B01MEE4UYL/'
    ]

    def parse(self, response):
        item = AmazonItem()
        selector = response.selector

        #title = selector.xpath('// *[ @ id = "productTitle"]/text()').extract_first().strip()
        title = selector.css('span[id="productTitle"]::text').extract_first().strip()
        reviews = selector.css('span[id="acrCustomerReviewText"]::text').extract_first().strip()
        answers = selector.css('a[id="askATFLink"] .a-size-base::text').extract_first().strip()
        stars = selector.css('.a-declarative .a-icon-alt::text').extract_first().strip()
        price = selector.css('span[id="priceblock_saleprice"]::text').extract_first().strip()

        # print('+++++++++')
        # print(title)
        # print(reviews)
        # print(answers)
        # print(stars)
        # print(price)
        # print('===========')
        item['title'] = title
        item['reviews'] = reviews
        item['answers'] = answers
        item['stars'] = stars
        item['price'] = price

        yield item
class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    base_url = 'http://www.amazon.com'
    load_page = 1
    start_urls = [
        'https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=3d+pen'
    ]

    def parse(self, response):
        # with open('body', 'wb') as f:
        #     f.write(response.body)
        item = AmazonItem()
        selector = response.selector
        products = selector.css('.s-result-item')
        for pro in products:
            isPro = pro.css('.a-fixed-left-grid').extract()
            if (len(isPro)<1):
                continue

            title = pro.css('h2.s-access-title::attr(data-attribute)').extract_first()
            asin = pro.css('::attr(data-asin)').extract_first()
            att_id = pro.css('::attr(id)').extract_first()

            print('+'*10)
            print(att_id)
            print(title)
            print(asin)
            print('='*10)


        self.load_page = self.load_page + 1

        next_pages = selector.css('.pagnNext::attr(href)')

        if next_pages and self.load_page<3:
            page_url = self.base_url + next_pages[0].extract()
            print(page_url)
            yield scrapy.Request(page_url, callback=self.parse)

'''