# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser

class LoginGithubSpider(scrapy.Spider):
    name = "login_github"
    allowed_domains = ["github.com"]

    def __init__(self, *args, **kwargs):
        super(LoginGithubSpider, self).__init__(*args, **kwargs)
        self.url = 'https://github.com'
        self.start_url = 'https://github.com/login'
        self.login_url = 'https://github.com/session'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': 1,
        }
        self.data = {
            'login': 'xxoo',
            'password': 'ooxx',
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
            method = 'POST',
            formdata = self.data,
            headers = self.headers,
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

