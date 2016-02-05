# 爬取stackoverflow网站问题页首页所有链接页面的相应信息。

import scrapy

class StackOverFlowSpider(scrapy.Spider):
    name = 'stackoverflow'
    start_urls = ["http://stackoverflow.com/questions"]

    def parse(self, response):
        for href in response.css(".question-summary h3 a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback = self.parse_content)

    def parse_content(self, response):
        yield {
            "title": response.css("#question-header a::text").extract()[0],
            "vote": response.css(".question .vote-count-post::text").extract()[0],
            "content": response.css(".question .post-text").extract()[0],
            "tags": response.css(".post-taglist .post-tag::text").extract()
        }
