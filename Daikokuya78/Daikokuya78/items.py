# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Daikokuya78Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 描述
    title = scrapy.Field()
    detail_url = scrapy.Field()

    # 价格
    price = scrapy.Field()
    official_retail_price = scrapy.Field()

    currency = scrapy.Field()
    official_price = scrapy.Field()
    condition_new_price = scrapy.Field()

    # id
    sku = scrapy.Field()
    product_id = scrapy.Field()

    # 基本属性
    brand = scrapy.Field()
    model = scrapy.Field()
    material = scrapy.Field()
    color = scrapy.Field()
    size = scrapy.Field()
    sex = scrapy.Field()
    type = scrapy.Field()
    subtype = scrapy.Field()
    origin_condition = scrapy.Field()

    # 图片
    photo_list = scrapy.Field()

    # 时间信息
    sell_date = scrapy.Field()  # 销售时间
    sold_date = scrapy.Field()  # 售出时间
    crawl_date = scrapy.Field()  # 爬取时间

    # 网站信息
    web_name = scrapy.Field()
    web_info = scrapy.Field()

    # 网站的实体店信息
    web_store_info = scrapy.Field()

    # 供应商信息
    vendor_info = scrapy.Field()

    exchange_rate = scrapy.Field()





