import scrapy
from amazon.items import AmazonItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domians = ['amazon.com']
    start_urls = ['https://www.amazon.com/gp/product/B01BLQ24IW/']

    def parse(self, response):
        #print(response.body)
        filename = 'test'
        #with open(filename, 'wb') as f:
         #   f.write(response.body)
        item = AmazonItem()
        selector = response.selector
        #products = selector.xpath('/div[@id="centerCol"]')
        #for info in products:
        #    title = info.xpath('// *[ @ id = "productTitle"]/text()').extract()[0]
        #    print('+++++++')
        #    print(title)
        #    print('========')
        #title = selector.xpath('// *[ @ id = "productTitle"]/text()').extract_first().strip()
        title = selector.css('span[id="productTitle"]::text').extract_first().strip()
        reviews = selector.css('span[id="acrCustomerReviewText"]::text').extract_first().strip()
        answers = selector.css('a[id="askATFLink"] .a-size-base::text').extract_first().strip()
        stars = selector.css('.a-declarative .a-icon-alt::text').extract_first().strip()
        price = selector.css('span[id="priceblock_saleprice"]::text').extract_first().strip()
        print('+++++++++')
        print(title)
        print(reviews)
        print(answers)
        print(stars)
        print(price)
        print('===========')
        # print(title_css)
        # print('xxxxxxxxxxx')