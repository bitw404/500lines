# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser

class LoginAmazonSpider(scrapy.Spider):
    name = "login_amazon"
    allowed_domains = ["amazon.com"]
    
    def __init__(self, *args, **kwargs):
        super(LoginAmazonSpider, self).__init__(*args, **kwargs)
        # 登录页的url地址
        self.url = 'https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_youraccount_signout%26signIn%3D1%26useRedirectOnSuccess%3D1'
        self.data = {
            'email': 'xx@oo.com',
            'password': 'xxoo'
        }
        self.headers = {
            # 直接将浏览器中监控到的登录请求headers复制到这里即可。
            # 去掉Content-Length，否则会出错。
            # User-Agent的设置必须放到settings中去。
            # 'Content-Length':'1616'
            # 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Cookie':'x-wl-uid=1V41RvsEj7u/Dzmr0WmC32N+Tx5W/ABxzYT7049QN6G3MHKjK5YOzpcq8hWfL1yv+dDidX1WE4FoKNfdNzTfHzNsv3Kfx6sB5xfWW9Lgb+w+6xmXPvpHjTHcPhqf4Scvh0AfwhuQ1aV0=; session-token=lnZEWTig/hlESGvWOr2WSzjXnD2FSAA67DuCiheMOeZVyTLxbEAKQRe3EitIMz6ito8U600uyDIcMDx19oqpJV2da+seWpYgpGl30ZA6XpGgwIVsk0dt7eo9ioCZHdJglR+fzgAYNOgs3Z072oxVl4i+GlCduNEuMi5mtXFHbYcSItB18SaoOilX6icDYVotjEM1nTslXPmlcblTBoP8oybEKOyBemO/Tn3VblIC4FoXeRczDBAEVDydUAAsXY4m; skin=noskin; session-id-time=2082787201l; session-id=191-0998353-2012054; ubid-main=184-7180606-1479062; csm-hit=s-8CYMZECCJ2WXM2NPE7T2|1455685340501',
            'Host':'www.amazon.com',
            'Origin':'https://www.amazon.com',
            'Referer':'https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_custrec_signin',
            'Upgrade-Insecure-Requests':1,
        }

    def start_requests(self):
        return [
            Request(url=self.url, callback=self.parse_welcome)
        ]

    def parse_welcome(self, response):
        return FormRequest.from_response(response, formdata=self.data, headers=self.headers, callback=self.after_login)

    def after_login(self, response):
        open_in_browser(response,)
