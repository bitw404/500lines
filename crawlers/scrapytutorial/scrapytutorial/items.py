# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    score = scrapy.Field()
    hot = scrapy.Field()
    wcount = scrapy.Field()
    imgurls = scrapy.Field()

class ArticleItem(scrapy.Item):
    book = scrapy.Field()
    title = scrapy.Field()
    utime = scrapy.Field()
    wcount = scrapy.Field()
    content = scrapy.Field()

class CommentItem(scrapy.Item):
    book = scrapy.Field()
    username = scrapy.Field()
    degree = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()

