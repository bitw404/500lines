# -*- coding: utf-8 -*-

BOT_NAME = 'scrapytutorial'
SPIDER_MODULES = ['scrapytutorial.spiders']
NEWSPIDER_MODULE = 'scrapytutorial.spiders'

# LOG_FILE = 'me.log'
LOG_LEVEL = 'INFO'

# 同时处理pipeline的最大并发数
CONCURRENT_ITEMS = 1000
# 同时发起网络请求的最大并发数
CONCURRENT_REQUESTS = 100
# 每个网站, 最大请求并发数
CONCURRENT_REQUESTS_PER_DOMAIN = 100
# 默认为0
# 每个IP最大请求并发数，如果不为0则覆盖CONCURRENT_REQUESTS_PER_DOMAIN
# 即请求并发数不再针对网站，而是针对IP，对DOWNLOAD_DELAY的影响也将针对每个ip。
CONCURRENT_REQUESTS_PER_IP = 0

DOWNLOAD_DELAY=0.5
DOWNLOAD_TIMEOUT = 10

# DOWNLOADER_MIDDLEWARES = {
#    'scrapytutorial.misc.middlewares.CustomHTTPProxyMiddleware': 543,
#    'scrapytutorial.misc.middlewares.CustomUserAgentMiddleware': 544,
# }

ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'scrapytutorial.pipelines.NovelPipeline': 300,
}

# imgurls对应的是items中的field
IMAGES_URLS_FIELD = 'imgurls'
IMAGES_STORE = r'.'
# IMAGES_THUMBS = {
    # 'small': (50, 50),
    # 'big': (270, 270),
# }

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4,ja;q=0.2',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
}
