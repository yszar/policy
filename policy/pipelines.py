# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.files import FilesPipeline
import scrapy
from os.path import join


class PolicyPipeline(object):
    def process_item(self, item, spider):
        return item


class MyFilesPipeline(FilesPipeline):

    # 重写get_media_requests方法
    def get_media_requests(self, item, info):
        for file_url in item['file_url']:
            yield scrapy.Request(file_url, meta={'item': item})

    # 重写file_path方法
    def file_path(self, request, response=None, info=None):
        # path = urlparse(request.url).path
        item = request.meta['item']  # 通过meta把item值传递过来
        # src_contents = item['src_contents']  # 获取目录名
        filename = item['filename']   # 获取文件名

        return join(filename)
