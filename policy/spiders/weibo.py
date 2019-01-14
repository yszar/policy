# -*- coding: utf-8 -*-
import scrapy


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    start_urls = ['https://s.weibo.com/weibo/iphone?topnav=1&wvr=6&b=1']

    def parse(self, response):
        a = 1
        pass
