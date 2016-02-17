# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser

class LoginDoubanSpider(scrapy.Spider):
    name = "login_douban"
    allowed_domains = ["douban.com"]

    def __init__(self, *args, **kwargs):
        super(LoginDoubanSpider, self).__init__(*args, **kwargs)
        self.url = 'https://www.douban.com'
        self.start_url = 'https://www.douban.com/accounts/login'
        self.login_url = 'https://accounts.douban.com/login'
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate',
            'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'upgrade-insecure-requests': '1',
        }
        self.data = {
            'form_email': 'xxoo',
            'form_password': 'ooxx',
        }

    def start_requests(self):
        return [Request(
            url = self.start_url,
            callback = self.parse_login,
        )]

    def parse_login(self, response):
        return FormRequest.from_response(
            response,
            url = self.login_url,
            formdata = self.data,
            headers = self.headers,
            method = 'POST',
            callback = self.after_login,
        )

    def after_login(self, response):
        return Request(
            url = self.url,
            callback = self.parse_index,
            dont_filter = True,
        )

    def parse_index(self, response):
        open_in_browser(response)