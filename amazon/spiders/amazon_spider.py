import scrapy
from amazon.items import AmazonItem

'''
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
'''

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