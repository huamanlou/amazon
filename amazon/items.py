# -*- coding: utf-8 -*-
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    #标题
    title = scrapy.Field()
    #asin
    asin = scrapy.Field()
    #品牌名称
    brand = scrapy.Field()
    #卖点
    bullet_point = scrapy.Field()
    #是否亚马逊发货
    isPrime = scrapy.Field()
    #销量
    sales = scrapy.Field()
    #库存
    stock = scrapy.Field()
    #评价得分，星级
    stars = scrapy.Field()
    #评价总数
    reviews = scrapy.Field()
    #问题总数
    questions = scrapy.Field()
    #商品销售价格
    price = scrapy.Field()
    #跟卖数量
    to_sell = scrapy.Field()
    #分类销量排名
    bsr = scrapy.Field()
    #创建日期
    ctime = scrapy.Field()
