# --- 基础功能：
# http://www.8kana.com/ 不可能的世界小说网站爬虫项目。
# Tornado实现异步爬取数据。使用队列的方式控制并发数量。
# pyquery解析dom树。
# ajax逆向工程，实现ajax动态数据爬取。
# 使用motor存储数据到mongodb。

# 模拟登陆功能，解决部分页面需要登录才能爬取的问题。

from tornado import gen, httpclient, ioloop, queues
from pyquery import PyQuery as pq
import time
import json
from motor.motor_tornado import MotorClient

pages = ["http://www.8kana.com/home/bookclass/bookshelf/0-0-0-0-0-0-0-1-2?page=" + str(index + 1) + ".html" for index in range(48)]

client = MotorClient("localhost", 27017)
db = client.xsdb
collection_novel = db.novel

@gen.coroutine
def get_perpage_comments(id, page_index):
    try:
        # 逆向模拟ajax get请求
        html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/home/comment/list?item=1&id=" + str(id) + "&type=2&SubType=0&page=" + str(page_index))
    except Exception as e:
        print("get_perpage_comments failed.", e)
        return []
        
    comments = []
    d = pq(html.body.decode("utf-8"))
    links = d(".essenceBook_C_Title_font").map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
    
    for link in links:
        try:
            html = yield httpclient.AsyncHTTPClient().fetch(link)
            d = pq(html.body.decode("utf-8"))
            comments.append(d(".BookDetails_In_p").html())
        except Exception as e:
            print("get comment with link failed.", e)
            continue
    return comments
    
@gen.coroutine
def get_comments(id):
    comments = []
    try:
        # 逆向模拟ajax post请求
        # allow_nonstandard_methods = True    允许post请求body为None
        html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/home/ajax/ajaxGetBookCommentNum/" + id, method = "POST", allow_nonstandard_methods = True)
    except Exception as e:
        print("get commnet number failed.", e)
        return []

    comment_number = json.loads(html.body.decode("utf-8"))["CommentNum"]
    if comment_number == 0:
        return []
    if comment_number <= 10:
        comment_page = 1
    elif comment_number % 10 != 0:
        comment_page = comment_number // 10 + 1
    else:
        comment_page = comment_number // 10

    for index in range(comment_page):
        perpage_comments = yield get_perpage_comments(id, index + 1)
        comments.extend(perpage_comments)
    return comments

@gen.coroutine
def get_content_by_link(link):
    try:
        html = yield httpclient.AsyncHTTPClient().fetch(link)
    except Exception as e:
        print("get_content_by_link failed.", e)
        return ()

    d = pq(html.body.decode("utf-8"))
    return d(".readbook_title").text(), d(".myContent").text()

@gen.coroutine
def get_contents(id):
    contents = []
    try:
        html = yield httpclient.AsyncHTTPClient().fetch("http://www.8kana.com/list/" + id + ".html")
    except Exception as e:
        print("get contents link failed.", e)
        return []

    d = pq(html.body.decode("utf-8"))
    links = d(".informList a").filter(lambda i, e: pq(e).attr("href").startswith("/read")).map(lambda i, e: "http://www.8kana.com" + pq(e).attr("href"))
    for link in links:
        content = yield get_content_by_link(link)
        contents.append(content)
    return contents
    
@gen.coroutine
def make_book(d, id):
    comments = yield get_comments(id)
    contents = yield get_contents(id)
    return {
        "title": d(".bookContain_l_conh2 h2").text(),
        "author": d("a.authorName").text(),
        "score": d(".bookContain_r1_upsp span").text(),
        "hot_degree": d("span.imformPopularity").eq(0).text(),
        "word_number": d("span.imformPopularity").eq(1).text(),
        "fuck_times": d("span.imformPopularity").eq(2).text(),
        "comments": comments,
        "contents": contents
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
            yield collection_novel.insert(book)
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