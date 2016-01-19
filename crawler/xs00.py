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

db = TinyDB(os.path.abspath(os.path.dirname(__file__)) + "/db.json")
book_index = 1

@gen.coroutine
def books_handler(links):
    q = queues.Queue()
    for link in links:
        yield q.put(link)

    @gen.coroutine
    def handle_book_by_link():
        global book_index
        link = yield q.get()
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            db.insert({
                "title": d(".bookContain_l_conh2 > h2").text(),
                "author": d(".authorName").text(),
                "score": d(".bookContain_r1_upsp span").text()
            })
            print("book {} done:".format(book_index), d(".bookContain_l_conh2 > h2").text())
        except Exception as e:
            print("get_book_by_link failed.", e)
        finally:
            book_index += 1
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield handle_book_by_link()

    for _ in range(10):
        worker()
    yield q.join()

@gen.coroutine
def get_links():
    links = []
    q = queues.Queue()
    for page in ["http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=" + str(index + 1) + ".html" for index in range(49)]:
        yield q.put(page)

    @gen.coroutine
    def get_perpage_links():
        page = yield q.get()
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(page)
            d = pq(html.body.decode("utf-8"))
            return d(".right.classPage_books_B_R > a").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
        except Exception as e:
            print("get_perpage_links failed.", e)
            return []
        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            perpage_links = yield get_perpage_links()
            links.extend(perpage_links)

    for _ in range(10):
        worker()
    yield q.join()
    return links

@gen.coroutine
def main():
    start = time.time()
    links = yield get_links()
    yield books_handler(links)
    print("done in {} seconds.".format(time.time() - start))

if __name__ == "__main__":
    ioloop.IOLoop.current().run_sync(main)