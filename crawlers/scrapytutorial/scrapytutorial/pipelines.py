# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapytutorial.items import BookItem, ArticleItem, CommentItem

class NovelPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['8kana']
        self.book_col = self.db.books
        self.article_col = self.db.articles
        self.comment_col = self.db.comments

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            self.book_col.insert(dict(item))
        if isinstance(item, ArticleItem):
            self.article_col.insert(dict(item))
        if isinstance(item, CommentItem):
            self.comment_col.insert(dict(item))
