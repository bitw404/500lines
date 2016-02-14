# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from demo.items import InfoItem
from demo.items import DetailItem

class BookSpider(CrawlSpider):
    name = 'book'
    allowed_domains = ['www.8kana.com']
    start_urls = ['http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=' + str(index + 1) + '.html' for index in range(1)]

    rules = (
        Rule(LinkExtractor(restrict_xpaths = '//a[starts-with(@href, "/book")]'), callback='parse_info', follow=True),
        Rule(LinkExtractor(restrict_xpaths = '//a[starts-with(@href, "/list")]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths = '//a[starts-with(@href, "/read")]'), callback='parse_detail'),
    )

    def parse_info(self, response):
        info = InfoItem()
        info['title'] = response.css('.bookContain_l_conh2 > h2::text').extract_first()
        info['author'] = response.css('.authorName::text').extract_first()
        info['score'] = response.css('.bookContain_r1_upsp > span::text').extract_first()
        info['hot'] = response.css('.imformPopularity::text').extract_first()
        return info

    def parse_detail(self, response):
        detail = DetailItem()
        detail['book'] = response.xpath('//a[starts-with(@href, "/book")]/text()').extract_first().strip()
        detail['title'] = response.css('.readbook_title::text').extract_first()
        detail['date'] = response.css('.readbook_ul > li::text')[1].re(r'[-\d]+')[0].strip()
        detail['wcount'] = response.css('.readbook_ul > li::text')[2].re(r'\d+')[0].strip()
        return detail
