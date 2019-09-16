# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AucnetItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    product_id = scrapy.Field()  # 产品的id

    title = scrapy.Field()  # 描述
    detail_url = scrapy.Field()  # 商品的链接

    price = scrapy.Field()  # 商品的价格
    original_price = scrapy.Field()  # 商品的原价
    official_retail_price = scrapy.Field()  # 商品的官方价格
    currency = scrapy.Field()  # 货币的单位
    official_price = scrapy.Field()
    condition_new_price = scrapy.Field()

    sku = scrapy.Field()  # 网站名+产品的ID
    brand = scrapy.Field()  # 商品的品牌
    model = scrapy.Field()
    material = scrapy.Field()  # 材质
    color = scrapy.Field()  # 颜色
    size = scrapy.Field()  # 尺寸的大小
    sex = scrapy.Field()  # 性别
    type = scrapy.Field()  # 商品的类型
    subtype = scrapy.Field()  # 子包类型
    origin_condition = scrapy.Field()  # 商品的成色
    photo_list = scrapy.Field()  # 商品的图片
    sell_date = scrapy.Field()  # 销售时间
    sold_date = scrapy.Field()  # 售出时间
    crawl_date = scrapy.Field()  # 爬取时间
    web_name = scrapy.Field()  # 网站名
    web_info = scrapy.Field()  # 网站信息
    web_store_info = scrapy.Field()  # 网站的实体店信息
    data_ready = scrapy.Field()  #
    standard_condition = scrapy.Field()  # 标准成色
    exchange_rate = scrapy.Field()  # 汇率

    vendor_info = scrapy.Field()  #
    full_content = scrapy.Field()  #
    brand_id = scrapy.Field()  # 品牌的ID
