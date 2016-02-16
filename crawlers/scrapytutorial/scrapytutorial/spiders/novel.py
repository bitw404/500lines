# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapytutorial.items import BookItem, ArticleItem, CommentItem
import json

class NovelSpider(CrawlSpider):
    name = 'novel'
    allowed_domains = ['8kana.com']
    pages = 1
    start_urls = ['http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=' + str(index+1) + '.html' for index in range(pages)]

    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a[starts-with(@href, "/book")]'), callback='parse_book', follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[starts-with(@href, "/list")]'), follow=True),
        Rule(LinkExtractor(restrict_xpaths='//a[starts-with(@href, "/read")]'), callback='parse_article')
    )

    def parse_book(self, response):
        book = BookItem()
        book['_id'] = response.xpath('//a[starts-with(@href, "/list")]/@href').re(r'\d+')[0]
        book['title'] = response.css('.bookContain_l_conh2 > h2::text').extract_first()
        book['author'] = response.css('.authorName::text').extract_first()
        book['score'] = response.css('.bookContain_r1_upsp > span::text').extract_first()
        book['hot'] = response.css('.imformPopularity::text')[0].extract().strip()
        book['wcount'] = response.css('.imformPopularity::text')[1].extract().strip()
        yield Request(url='http://www.8kana.com/home/ajax/ajaxGetBookCommentNum/'+str(book['_id']), callback=self.parse_comment, meta={'book_id': book['_id']}, method='POST')
        yield book

    def _get_comment_page_num(self, num):
        if not isinstance(num, int) or num <= 0:
            return 0
        return num // 10 if (num % 10 == 0) else (num // 10 + 1)

    def parse_comment(self, response):
        book_id = response.meta['book_id']
        comment_page_num = self._get_comment_page_num(json.loads(response.body)['CommentNum'])
        for index in range(comment_page_num):
            yield Request(url='http://www.8kana.com/home/comment/list?item=1&type=2&SubType=0&id='+str(book_id)+'&page='+str(index+1), callback=self.parse_comment_links)

    def parse_comment_links(self, response):
        for link in ['http://www.8kana.com'+href for href in response.xpath('//a[starts-with(@href, "/community")]/@href').extract()]:
            yield Request(url=link, callback=self.parse_comment_detail)

    def parse_comment_detail(self, response):
        comment = CommentItem()
        comment['book'] = response.css('.sageCity_BookDetails_Head_R_bookName_T > a::attr("href")').re(r'\d+')[0].strip()
        comment['username'] = response.css('.sageCity_BookDetails_Name_T_a::text').extract_first()
        comment['degree'] = response.css('.sageCity_BookDetails_Name_span::text').extract_first()
        comment['title'] = response.css('.sageCity_BookDetails_Title_L::text').extract_first()
        yield comment

    def parse_article(self, response):
        article = ArticleItem()
        article['book'] = response.xpath('//a[starts-with(@href, "/book")]/@href').re(r'\d+')[0].strip()
        article['title'] = response.css('.readbook_title::text').extract_first()
        article['utime'] = response.css('.readbook_ul > li::text')[1].re(r'[\d-]+')[0].strip()
        article['wcount'] = response.css('.readbook_ul > li::text')[2].re(r'\d+')[0].strip()
        return article


