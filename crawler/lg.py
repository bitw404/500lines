# 拉钩网爬虫。
# Tornado实现异步爬取数据。使用队列的方式控制并发数量。
# 使用BeautifulSoup解析DOM树。
# ajax逆向工程，实现ajax动态数据爬取。
# 使用motor存储数据到mongodb。

from tornado import httpclient, gen, queues, ioloop
from bs4 import BeautifulSoup as Soup
from urllib.parse import urlencode
import json
import time
import re
from motor.motor_tornado import MotorClient

client = MotorClient('localhost', 27017)
db = client.lgdb
collection_jobs = db.jobs

concurrency = 10
base_url = 'http://www.lagou.com/jobs/'

pages = [{'url': 'http://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC', 'kd': '爬虫工程师', 'pn': index + 1} for index in range(30)]
pages.extend([{'url': 'http://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC', 'kd': 'Python', 'pn': index + 1} for index in range(30)])

def make_jobs(html):
    soup = Soup(html, 'lxml')
    jobs = {}
    # 职位名称
    jobs['job_title'] = soup.find(class_='job_detail').find('h1')['title']
    # 工作要求
    jobs['salary'], jobs['job_ciry'], jobs['experience'], jobs['degree'], jobs['job_type'] = (job_request.get_text(strip = True) for job_request in soup.find(class_='job_request').find('p').findAll('span'))
    # 发布时间
    jobs['publish_time'] = re.split('\s', soup.find(class_='publish_time').get_text(strip = True))[0]
    # 工作详情
    jobs['job_detail'] = str(soup.find(class_='job_bt'))
    
    # 公司名字
    jobs['company_name'] = soup.find(class_='job_company').find('dt').find(class_='fl').get_text('|', strip = True).split('|')[0]
    # 公司地址
    jobs['company_address'] = soup.find(class_='job_company').find('dd').find('div').get_text(strip = True)
    
    company_infos = soup.findAll(class_='c_feature')
    # 公司网址。
    jobs['company_url'] = company_infos[0].findAll('li')[2].find('a')['href']
    # 公司经营领域，移动互联网、电子商务、游戏。
    jobs['company_domain'] = company_infos[0].find('li').get_text('|', strip = True).split('|')[1]
    # 公司规模，200人。
    jobs['company_size'] = company_infos[0].findAll('li')[1].get_text('|', strip = True).split('|')[1]
    # 公司阶段，A轮B轮。
    jobs['company_stage'] = company_infos[1].find('li').get_text('|', strip = True).split('|')[1]

    return jobs

@gen.coroutine
def get_page_links(page):
    obj = {
        'kd': page['kd'],
        'pn': page['pn']
    }
    try:
        res = yield httpclient.AsyncHTTPClient().fetch(page['url'], method = 'POST', body = urlencode(obj))
        res = res.body.decode('utf-8')
        # 记录获取ajax数据成功的日志。
        print('---{}:{}'.format(page['kd'], page['pn']))
        results = json.loads(res)['content']['result']
        return [base_url + str(result['positionId']) + '.html' for result in results]
    except Exception as e:
        # 记录获取ajax数据失败的日志。
        print('!--{}:{}'.format(page['kd'], page['pn']))
        return []

@gen.coroutine
def get_job_infos(links):
    if len(links) == 0:
        return
    for link in links:
        try:
            res = yield httpclient.AsyncHTTPClient().fetch(link)
            html = res.body.decode('utf-8')
            jobs = make_jobs(html)
            # 将工作信息保存到数据库中
            yield collection_jobs.insert(jobs)
            # 记录获取工作详情页成功的日志。
            print(jobs['company_name'], link)
        except Exception as e:
            # 记录获取工作详情页失败的日志。
            print(failed, link)

@gen.coroutine
def main():
    q = queues.Queue()
    start = time.time()

    @gen.coroutine
    def get_jobs():
        page = yield q.get()
        try:
            links = yield get_page_links(page)
            yield get_job_infos(links)
        finally:
            q.task_done()

    @gen.coroutine
    def worker():
        while True:
            yield get_jobs()

    for page in pages:
        q.put(page)
    for _ in range(concurrency):
        worker()
    yield q.join()
    print('done in {} seconds.'.format(time.time() - start))

if __name__ == '__main__':
    ioloop.IOLoop.current().run_sync(main)