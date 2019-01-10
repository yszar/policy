# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PolicyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_url = scrapy.Field()  # 指定文件下载的连接
    file = scrapy.Field()  # 文件下载完成后会往里面写相关的信息
    # src_contents = scrapy.Field()  # 文件分类存储路径
    filename = scrapy.Field()  # 文件名

