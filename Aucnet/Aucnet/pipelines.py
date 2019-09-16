# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymysql
from Aucnet.settings import *


class AucnetPipeline(object):
    def process_item(self, item, spider):
        return item


class AucnetMysqlPipeline(object):

    def __init__(self):
       self.db = pymysql.connect(
           host=MYSQL_HOST,
           port=MYSQL_PORT,
           user=MYSQL_USER,
           password=MYSQL_PWD,
           database=MYSQL_DB,
           charset='utf8'
       )
       self.cursor = self.db.cursor()
       self.L = []

    def process_item(self, item, spider):
        keys = ['title', 'detail_url', 'price', 'original_price', 'official_retail_price', 'currency', 'sku',
                'product_id', 'brand', 'model',
                'material', 'color', 'size', 'sex', 'web_name', 'type', 'subtype', 'origin_condition', 'photo_list',
                'sell_date',
                'sold_date', 'crawl_date', 'standard_condition', 'web_info', 'web_store_info', 'vendor_info',
                'exchange_rate',
                'full_content', 'official_price', 'condition_new_price']
        for key in keys:
            if key not in item.keys():
                item[key] = ""
                if key is "price":
                    item[key] = 0
            value = item[key]
            if isinstance(value, list):
                try:
                    value = ','.join(value)
                except Exception as e:
                    print(e)
            elif isinstance(value, float):
                value = str(value)
            elif isinstance(value, dict):
                value = str(value)
            item[key] = value

        self.L.append([item['title'], item['detail_url'], item['price'], item['original_price'], item['official_retail_price'], item['currency'],
                        item['sku'], item['product_id'], item['brand'], item['model'], item['material'], item['color'], item['size'], item['sex'], item['web_name'],
                        item['type'], item['subtype'], item['origin_condition'], item['photo_list'], item['sell_date'], item['sold_date'], item['crawl_date'],
                        item['standard_condition'], item['web_info'], item['web_store_info'], item['vendor_info'], item['exchange_rate'], item['full_content'],
                       item['official_price'], item['condition_new_price']])
        if len(self.L) == 1000:
            self.bulk_insert_to_mysql(self.L)
            # 清空缓存
            del self.L[:]
        return item

    def bulk_insert_to_mysql(self, data):
        try:
            sql = 'insert into AllData (title, detail_url,price,original_price,official_retail_price,currency,sku,' \
                    'product_id,brand,model,material,color,size,sex,web_name,type,subtype,origin_condition,photo_list,sell_date,' \
                    'sold_date,crawl_date,standard_condition,web_info,web_store_info,vendor_info,exchange_rate,full_content,official_price, condition_new_price) ' \
                    'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            self.cursor.executemany(sql, data)
            self.db.commit()
        except Exception as e:
            print(e)
            self.db.rollback()

    def close_spider(self, spider):
        self.bulk_insert_to_mysql(self.L)
        self.db.commit()
        self.cursor.close()
        self.db.close()