# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LeprixItem(scrapy.Item):
    # 描述
    title = scrapy.Field()
    detail_url = scrapy.Field()

    # 价格
    price = scrapy.Field()
    original_price = scrapy.Field()
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


    # 图片
    photo_list = scrapy.Field()

    # 时间信息
    sell_date = scrapy.Field()  # 销售时间
    sold_date = scrapy.Field()  # 售出时间  -->推理出: status
    crawl_date = scrapy.Field()  # 爬取时间
#    crawl_times = scrapy.Field()  # 爬取的序号

    # -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -   -

    # 网站信息

    web_info = scrapy.Field()

    '''web_info = {"name":"","country":"","city":"","address":"","phone":"","language":"","image_resolution":"","pslw":"","location":{"longitude":"","Latitude":""}}'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # 网站的实体店信息
    web_store_info = scrapy.Field()
    '''web_store_info =
        [ {"name":"商店1" , "address" : "" ,"phone":"" , "city" : "" , "country" : "" , "location":{"longitude":"","Latitude":""}},
        {"name":"商店2" , "address" : "" ,"phone":"" , "city" : "" , "country" : "" , "location":{"longitude":"","Latitude":""}}]'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # 供应商信息
    vendor_info = scrapy.Field()
    '''  vendor_info = {"name":"","country":"","city":"","address":"","page":"","phone":"","word":"","store":"","location":{"longitude":"","Latitude":""}}'''
    official_retail_price = scrapy.Field()

    web_name = scrapy.Field()

    data_ready = scrapy.Field()#  # 该条数据是否可以做比价和销量  ——  (新增)
    origin_condition =  scrapy.Field()## 源网站成色      ——   原来字段名  condition
    standard_condition =  scrapy.Field()## 标准成色     ——   (新增)
    business_type = scrapy.Field()#(可选{1: 新的, 2: 二手, 3: 混合[比例达到30 %]})  # 经营种类       ——      原来的字段名  :  PSW
    exchange_rate = scrapy.Field()
    full_content = scrapy.Field()# # 全文   ——   (新增)


