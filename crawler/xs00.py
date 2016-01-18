# --- 基础功能：

# http://www.8kana.com/ 不可能的世界小说网站爬虫项目。
# Tornado实现异步爬取数据。使用队列的方式控制并发数量。
# pyquery解析dom树。
# 使用TinyDB存储数据。

from tornado import gen, httpclient, ioloop, queues
from pyquery import PyQuery as pq
from tinydb import TinyDB
import os.path
import time
import json

pages = ["http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=" + str(index + 1) + ".html" for index in range(48)]
db = TinyDB(os.path.abspath(os.path.dirname(__file__)) + "/db.json")
    
@gen.coroutine
def make_book(d, id):
    return {
        "title": d(".bookContain_l_conh2 h2").text(),
        "author": d("a.authorName").text(),
        "score": d(".bookContain_r1_upsp span").text(),
        "hot_degree": d("span.imformPopularity").eq(0).text(),
        "word_number": d("span.imformPopularity").eq(1).text(),
        "fuck_times": d("span.imformPopularity").eq(2).text()
    }

@gen.coroutine
def get_book_links(page):
    try:
        html = yield httpclient.AsyncHTTPClient().fetch(page)
        d = pq(html.body.decode("utf-8"))
        return d(".right.classPage_books_B_R").children("a").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
    except Exception as e:
        print("get_book_links Exception", e)
        return []

@gen.coroutine
def get_book_infos(links):
    for link in links:
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            id = link.split("http://")[1].split("/")[2].split(".")[0]
            book = yield make_book(d, id)

            # 这里进行最终的数据处理
            if not book:
                continue
            db.insert(book)
            print("{} done.".format(book["title"]))

        except Exception as e:
            print("get_book_infos Exception", e)

@gen.coroutine
def main():
    @gen.coroutine
    def get_books():
        page = yield q.get()
        try:
            links = yield get_book_links(page)
            yield get_book_infos(links)
        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield get_books()

    start = time.time()
    q = queues.Queue()
    for page in pages:
        q.put(page)
    for _ in range(10):
        worker()
    yield q.join()
    print("done in {} seconds.".format(time.time() - start))

if __name__ == "__main__":
    ioloop.IOLoop.current().run_sync(main)