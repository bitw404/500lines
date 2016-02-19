# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser
from scrapytutorial.settings import HEADERS

class LoginZhihuSpider(scrapy.Spider):
    name = "login_zhihu"
    allowed_domains = ["zhihu.com"]
    start_urls = ['https://www.zhihu.com/#signin']
    def __init__(self, *args, **kwargs):
        super(LoginZhihuSpider, self).__init__(*args, **kwargs)
        self.login_url = 'https://www.zhihu.com/login/phone_num'
        self.zhihu_url = 'https://www.zhihu.com'
        self.data = {
            'phone_num': 'xxoo',
            'password': 'ooxx',
        }
    def parse(self, response):
        return FormRequest.from_response(
            response,
            url = self.login_url,
            method = 'POST',
            formdata = self.data,
            headers = HEADERS,
            callback = self.after_login,
            meta = {'cookiejar': 1},
        )
    def after_login(self, response):
        return Request(
            url = self.zhihu_url, 
            callback = self.end_login, 
            dont_filter = True, 
            meta = {'cookiejar': response.meta['cookiejar']}
        )
    def end_login(self, response):
        open_in_browser(response)