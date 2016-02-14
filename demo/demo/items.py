# -*- coding: utf-8 -*-

# Define here the models for your scraped items

import scrapy

class InfoItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    score = scrapy.Field()
    hot = scrapy.Field()

class DetailItem(scrapy.Item):
    book = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    wcount = scrapy.Field()
    content = scrapy.Field()
