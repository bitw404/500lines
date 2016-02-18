# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.utils.response import open_in_browser

# 验证码处理思路，就和这个类似。
class PlayImgSpider(scrapy.Spider):
    name = "play_img"
    allowed_domains = ["8kana.com"]
    start_urls = (
        'http://www.8kana.com/book/10027.html',
    )

    def parse(self, response):
        return Request(url = 'http://c.8kana.com/201509/100/27/10027_916b5_37_m.jpg', callback = self.parse_img)

    def parse_img(self, response):
        with open('xxoo.png', 'wb') as fp:
            fp.write(response.body)
        raw_input('请输入随便神马东东:')
        return Request(url = 'http://www.8kana.com', callback = self.game_over)

    def game_over(self, response):
        open_in_browser(response)
