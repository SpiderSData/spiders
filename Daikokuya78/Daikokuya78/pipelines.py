# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import time
import os
import pymysql
import scrapy

from Daikokuya78.settings import *
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline


class Daikokuya78Pipeline(object):
    def process_item(self, item, spider):
        # print()
        return item


class Daikokuya78MysqlPipeline(object):
    data_list = list()

    def open_spider(self, spider):
        self.f = open(str(spider.name) + 'mysqltest.txt', 'wb')
        self.db = pymysql.connect(host=MYSQL_HOST,
                                  user=MYSQL_USER,
                                  port=MYSQL_PORT,
                                  passwd=MYSQL_PWD,
                                  db=MYSQL_DB,
                                  charset='utf-8')
        self.cursor = self.db.cursor()

    def bulk_insert_to_mysql(self, bulkdata):
        try:
            sql = 'insert into AllData (title, detail_url,price,original_price,official_retail_price,currency,sku,' \
                  'product_id,brand,model,material,color,size,sex,web_name,type,subtype,origin_condition,photo_list,sell_date,' \
                  'sold_date,crawl_date,standard_condition,web_info,web_store_info,vendor_info,exchange_rate,full_content,official_price,condition_new_price) ' \
                  'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)'
            self.cursor.connection.ping(True)
            self.cursor.executemany(sql, bulkdata)
            self.db.commit()
        except Exception as e:
            self.f.write(str(e) + '\n')
            self.db.rollback()

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
                item[key] = ''
                if key is 'price':
                    item[key] = 0
            value = item[key]
            if isinstance(value, list):
                try:
                    value = ','.join(value)
                except Exception as e:
                    value = str(value)
            elif isinstance(value, float):
                value = str(value)
            elif isinstance(value, dict):
                value = str(value)
            item[key] = value

        self.data_list.append([item['title'], item['detail_url'], item['price'], item['original_price'], item['official_retail_price'],
                               item['currency'], item['sku'], item['product_id'], item['brand'], item['model'], item['material'],
                               item['color'], item['size'], item['sex'], item['web_name'], item['type'], item['subtype'],
                               item['origin_condition'], item['photo_list'], item['sell_date'], item['sold_date'],
                               item['crawl_date'], item['standard_condition'], item['web_info'], item['web_store_info'],
                               item['vendor_info'], item['exchange_rate'], item['full_content'], item['official_price'],
                               item['condition_new_price']])

        if len(self.data_list) == 3000:
            self.bulk_insert_to_mysql(self.data_list)
            # 清空data_list
            del self.data_list[:]
        return item

    def close_spider(self, spider):
        self.bulk_insert_to_mysql(self.data_list)
        self.cursor.close()
        self.db.close()


class Daikokuya78CsvPipeline(object):
    def open_spider(self, spider):
        brand_name = spider.name
        # if updateBrandName(spidername):
        #     global brand_name
        #     brand_name = updateBrandName(spidername)

        # 创建csv文件对象
        path_csv = local_path + time.strftime("%Y-%m-%d", time.localtime()) + '/'
        mkdir(path_csv)
        self.f = open(path_csv + brand_name + time.strftime('%Y-%m-%d', time.localtime()) + '.csv', 'wb')

        # 创建csv文件读写对象
        self.csv_exporter = CsvItemExporter(self.f)
        # 开始执行数据库item数据的读写操作
        self.csv_exporter.start_exporting()

    def process_item(self, item, spider):
        self.csv_exporter.export_item(item)
        return item

    def close_spider(self, spider):
        # 停止item数据的读写操作
        self.csv_exporter.finish_exporting()
        self.f.close()

class Daikokuya78ImagePipeline(ImagesPipeline):
    flag = 1
    images = ''

    def get_media_requests(self, item, info):
        if self.flag == 1:
            global brand_name
            brand_name = info.spider.name
            if not os.path.exists(local_path + 'Pipelines/OtherWebs/' + brand_name + '/Images/'):
                os.makedirs(local_path + 'Pipelines/OtherWebs/' + brand_name + '/Images/')
            self.images = os.listdir(local_path + 'Pipelines/OtherWebs/' + brand_name + '/Images/')
            self.flag = 0
        if item['sku'] in self.images:
            return
        for photo_url in item['photo_list']:
            yield scrapy.Request(photo_url)

    def file_path(self, request, response=None, info=None):
        url = request.url

        # 商品的id
        product_id = re.findall(r'#id=(.{0, 150})&v_', url)[0]
        product_image_num = re.findall(r'&v_(\d+)', url)[0]
        return '%s/' % brand_name + 'Images' + '/%s' % product_id + '/%s' % product_image_num + '.jpg'

    def item_completed(self, results, item, info):
        return item

def mkdir(path):
    path = path.strip()
    path = path.rstrip('\\')

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        print (path+' Directory or file created successfully!')
        return True
    else:
        print (path+' Directory or file already exists!')
        return False