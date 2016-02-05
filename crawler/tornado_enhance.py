# 增加功能：
# 1、评论ajax动态数据爬取。逆向分析ajax数据请求。
# 2、小说内容数据爬取。
# 3、使用motor异步存储数据到mongodb。

from tornado import ioloop, httpclient, gen, queues
from pyquery import PyQuery as pq
from motor.motor_tornado import MotorClient
import time
import json

client = MotorClient("localhost", 27017)
db = client["8kana"]
c_books = db.books

@gen.coroutine
def get_comments(d):
    comments = []
    id = d(".chapter_con_more > a").attr("href").split("/")[2].split(".")[0]
    try:
        links = []
        html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/home/ajax/ajaxGetBookCommentNum/" + str(id), method = "POST", allow_nonstandard_methods = True)
        comment_num = int(json.loads(html.body.decode("utf-8"))["CommentNum"])
        page_num = comment_num // 10 if comment_num % 10 == 0 else comment_num // 10 + 1

        for page in range(page_num):
            html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/home/comment/list?item=1&id=" + str(id) + "&type=2&SubType=0&page=" + str(page + 1))
            d = pq(html.body.decode("utf-8"))
            page_links = d(".clearfix.essenceBook_C_Title > a").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
            links.extend(page_links)
        
        for link in links:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            comments.append({
                "user": d(".left.sageCity_BookDetails_Name_T_a.manColor").text(),
                "title": d(".left.sageCity_BookDetails_Title_L").text(),
                "content": d(".BookDetails_In_p").html()
            })

        return comments
    except Exception as e:
        print("get comments failure.")
        return []

@gen.coroutine
def get_contents(d):
    contents = []
    id = d(".chapter_con_more > a").attr("href").split("/")[2].split(".")[0]
    try:
        html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/list/" + str(id) + ".html")
        d = pq(html.body.decode("utf-8"))
        links = d(".nolooking > a").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))

        for link in links:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            contents.append({
                "title": d(".readbook_title").text(),
                "content": d(".myContent").html()
            })

        return contents
    except Exception as e:
        print("get contents failure.")
        return []

@gen.coroutine
def make_book(d):
    comments = yield get_comments(d)
    contents = yield get_contents(d)
    return {
        "title": d(".bookContain_l_conh2 > h2").text(),
        "author": d(".authorName").text(),
        "score": d(".bookContain_r1_upsp > span").text(),
        "hot": d(".imformPopularity").eq(0).text(),
        "type": d(".bookContain_l_consp1").text(),
        "comments": comments,
        "contents": contents
    }

@gen.coroutine
def get_links():
    links = []
    q = queues.Queue()
    for page in ["http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=" + str(index + 1) + ".html" for index in range(52)]:
        yield q.put(page)

    @gen.coroutine
    def get_page_links():
        page = yield q.get()
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(page)
            d = pq(html.body.decode("utf-8"))
            return d(".right.classPage_books_B_R > a").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
        except Exception as e:
            print("get page links failure.")
            return []

    @gen.coroutine
    def worker():
        while True:
            page_links = yield get_page_links()
            links.extend(page_links)
            q.task_done()

    for _ in range(10):
        worker()
    yield q.join()
    return links

@gen.coroutine
def save_books(links):
    q = queues.Queue()
    for link in links:
        yield q.put(link)

    @gen.coroutine
    def get_book():
        link = yield q.get()
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            book = yield make_book(d)
            return book
        except Exception as e:
            print("get book failure.")
            return {}

    @gen.coroutine
    def worker():
        while True:
            book = yield get_book()
            if book:
                yield c_books.insert(book)
                print("get book {} done.".format(book["title"]))
            q.task_done()

    for _ in range(10):
        worker()
    yield q.join()

@gen.coroutine
def main():
    start = time.time()
    links = yield get_links()
    yield save_books(links)
    print("done in {} seconds.".format(time.time() - start))

if __name__ == "__main__":
    ioloop.IOLoop.current().run_sync(main)