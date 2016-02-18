import random
import logging
from scrapytutorial.agents import AGENTS
from scrapytutorial.proxies import PROXIES

class CustomHTTPProxyMiddleware:
    def process_request(self, request, spider):
        proxy = random.choice(PROXIES)
        logging.info('use proxy ' + proxy)
        request.meta['proxy'] = proxy

class CustomUserAgentMiddleware:
    def process_request(self, request, spider):
        agent = random.choice(AGENTS)
        logging.info('use agent ' + agent)
        request.headers['User-Agent'] = agent