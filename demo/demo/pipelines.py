# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from demo.items import InfoItem
from demo.items import DetailItem
from pymongo import MongoClient

class DemoPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['8kana']
        self.book_col = self.db['books']

    def process_item(self, item, spider):
        if isinstance(item, InfoItem):
            self.book_col.insert(dict(item))
        if isinstance(item, DetailItem):
            title = item['book']
            del item['book']
            self.book_col.update({'title': title}, {'$push': {'article': dict(item)}})
