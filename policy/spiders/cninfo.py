# -*- coding: utf-8 -*-
import scrapy
import re
import json
from ..items import PolicyItem
from ..param import *
import xlrd


from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import policy.pdftotext


class CninfoSpider(scrapy.Spider):
    def __init__(self):
        dispatcher.connect(policy.pdftotext.run, signals.engine_stopped)
        dispatcher.connect(policy.pdftotext.run, signals.spider_closed)

    name = 'cninfo'
    allowed_domains = ['cninfo.com.cn']

    # start_urls = [
    #     'http://www.cninfo.com.cn/new/fulltextSearch/full?' \
    #     'searchkey=' + '000100' + '%E5%85%AC%E5%8F%B8%E7%AB%A0%E7%' \
    #                                  'A8%8B&sdate=&edate=&isfulltext=false&sortName=' \
    #                                  'nothing&sortType=desc'
    # ]

    def start_requests(self):
        getfile = xlrd.open_workbook(XLSX)
        table = getfile.sheet_by_index(0)
        rows = table.nrows
        for i in range(1, rows):
            cell_vlaues = table.cell_value(i, 0)
            # for num in CODE:  # 迭代param.py中的所有CODE列表值
            # 将每个CODE带入参数获取api
            start_urls = 'http://www.cninfo.com.cn/new/fulltextSearch/full?' \
                         'searchkey=' + cell_vlaues + '%E5%85%AC%E5%8F%B8%E7%AB%A0%E7%' \
                                                      'A8%8B&sdate=&edate=&isfulltext=false&sortName=' \
                                                      'nothing&sortType=desc'
            src_contents = cell_vlaues  # 以CODE号码为文件名称
            yield scrapy.Request(url=start_urls, callback=self.parse,
                                 meta={'info': src_contents})

    def parse(self, response):
        src_contents = response.meta.get('info')
        pages = json.loads(response.text)['totalpages']
        for p in range(1, pages + 1):
            yield scrapy.Request(
                url=response.url + '&pageNum=' + str(p),
                callback=self.parse_get,
                meta={'info': src_contents})

    def parse_get(self, response):
        src_contents = response.meta.get('info')
        # api返回值中所有条目
        announcements = json.loads(response.text)['announcements']
        # pages = json.loads(response.text)['totalpages']
        for a in announcements:  # 迭代
            announcementtitle = a['announcementTitle']  # 获取title
            # 判断title中是否有括号,有则需要,无则抛弃
            if re.search('（.*）', announcementtitle):
                # api返回的url有302跳转,和跳转后的url拼接
                file_url = 'http://static.cninfo.com.cn/' + a['adjunctUrl']
                # 以该章程发布的年月日为文件名
                filename = src_contents + '_' + a['adjunctUrl'].split('/')[
                    1] + '.pdf'
                item = PolicyItem(
                    # src_contents=src_contents,
                    file_url=[file_url],
                    filename=filename
                )
                yield item
            else:
                continue
