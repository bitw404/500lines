# -*- coding: utf-8 -*-
import scrapy
from scrapy_base.items import ScrapyBaseItem

class DmozSpiderSpider(scrapy.Spider):
    name = "dmoz_spider"
    allowed_domains = ["dmoz.org"]
    start_urls = (
        'http://www.dmoz.org/Computers/Programming/Languages/Python/Books',
        'http://www.dmoz.org/Computers/Programming/Languages/Python/Resources'
    )

    def parse(self, response):
        infos = response.css('.directory-url li')
        for info in infos:
            item = ScrapyBaseItem()
            item['title'] = info.css('a::text').extract()[0]
            item['desc'] = info.css('::text').extract()[0]
            item['url'] = info.css('a::attr("href")').extract()[0]
            yield item
