# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
import pymysql
import json
import time
import os
import redis
import scrapy
import re
from Leprix.constant import brand_name,mkdir,local_path
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.images import ImagesPipeline
from Leprix.settings import IMAGES_STORE
from Leprix.settings import *


class LeprixImagePipeline(ImagesPipeline):  #--------第一处改


    # brand_name = ""  # -------第四处
    if not os.path.exists(str(local_path) + 'Pipelines/OtherWebs/' + str(brand_name) + '/Images/'):
        os.makedirs(str(local_path) + 'Pipelines/OtherWebs/' + str(brand_name) + '/Images/')
    images = os.listdir(str(local_path) + 'Pipelines/OtherWebs/' + str(brand_name) + '/Images/')
    def get_media_requests(self, item, info):
        if item['sku'] in self.images:
            return
        for photo_url in item['photo_list']:
            yield scrapy.Request(photo_url)

    def file_path(self, request, response=None, info=None):
        url = request.url
        #商品id
        product_id = re.findall(r'#id=(.{0,50})&v', url)[0]
        # #图片的序号
        product_image_num = re.findall(r'&v_(\d+)', url)[0]
        return '%s/' %brand_name + 'Images' + '/%s'% str(product_id) + '/%s' % (product_image_num) +'.jpg'

    def item_completed(self, results, item, info):
        return item


class LeprixCsvPipeline(object):               #----------第二处
    def open_spider(self, spider):
        # 创建csv文件对象
        print "------3213213213" * 30
        path_csv = local_path + 'AllSpiders/'+time.strftime('%Y-%m-%d', time.localtime())+'/'
        # path_csv = local_path+"Pipelines\\OtherWebs\\"+brand_name+"\\"+"Csv\\"  #第六处-------------


        mkdir(path_csv)

        self.f = open(path_csv + brand_name+time.strftime('%Y-%m-%d', time.localtime()) + '.csv', 'wb')
        #创建csv文件读写对象
        self.csv_exporter = CsvItemExporter(self.f)
        # 开始执行item数据的读写操作
        self.csv_exporter.start_exporting()

    def process_item(self, item, spider):
        self.csv_exporter.export_item(item)
        return item

    def close_spider(self, spider):
        # 停止item数据的读写操作
        self.csv_exporter.finish_exporting()
        self.f.close()


class LeprixPipeline(object):  #-------第三处
    def __init__(self):
        #                                           品牌名                         品牌名
        path_json = local_path+"Pipelines/OtherWebs/"+ brand_name+"/"+"Json/"   #第八处-----------
        # path_json = local_path+"Pipelines/OtherWebs\\" + brand_name+"\\"+"Json\\"   #第八处-----------
        print path_json
        print '098'*40
        mkdir(path_json)

        self.file = open(path_json+brand_name+'.json', 'wb')  #第九处------------

    def process_item(self, item, spider):
        # #过滤需要的字段
        dict_item = dict(item)

        data = {'title', 'detail_url', 'price', 'original_price', 'currency',
                'sku', 'product_id', 'brand', 'model', 'material', 'color', 'size',
                'sex', 'type', 'subtype', 'condition', 'photo_list', 'sell_date',
                'sold_date', 'crawl_date', 'crawl_times', 'web_info', 'web_store_info',
                'vendor_info', 'official_price', 'official_retail_price', 'web_name',
                'origin_condition','full_content','standard_condition','data_ready','web_name',
                'business_type', 'official_price', 'condition_new_price'
                }

        dict_item_fittler = {key:value for key, value in dict_item.items() if key in data}

        content = json.dumps(dict_item_fittler, ensure_ascii=False) + "\n"
        self.file.write(content)
        return item

    def close_spider(self, spider):
        self.file.close()

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

class CncompanyidSpiderFastPipeline(object):
    companylist = []

    def open_spider(self, spider):
        self.conn = pymysql.connect(host=MYSQL_HOST,
                                    user=MYSQL_USER,
                                    port=MYSQL_PORT,
                                    passwd=MYSQL_PWD,
                                    db=MYSQL_DB,
                                    charset='utf8mb4')
        self.cursor = self.conn.cursor()
        # 存入数据之前清空表：
        #self.cursor.execute('truncate table brandofftest')
        #self.conn.commit()

    # 批量插入mysql数据库
    def bulk_insert_to_mysql(self, bulkdata):
        print('alldata')
        # print(bulkdata)
        try:
            print 'the length of the data-------', len(self.companylist)
            sql = 'insert into AllData (title, detail_url,price,original_price,official_retail_price,currency,sku,' \
                  'product_id,brand,model,material,color,size,sex,web_name,type,subtype,origin_condition,photo_list,sell_date,' \
                  'sold_date,crawl_date,standard_condition,web_info,web_store_info,vendor_info,exchange_rate,full_content, official_price, condition_new_price) ' \
                  'values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            print('sql----------------------')
            print(sql)

            self.cursor.executemany(sql, bulkdata)
            self.conn.commit()
        except Exception as e:
            print('添加数据错误')
            print e
            self.conn.rollback()

    def process_item(self, item, spider):

        keys = ['title', 'detail_url', 'price', 'original_price','official_retail_price','currency', 'sku', 'product_id', 'brand', 'model',
                'material', 'color', 'size', 'sex', 'web_name','type', 'subtype', 'origin_condition', 'photo_list', 'sell_date',
                'sold_date', 'crawl_date','standard_condition',  'web_info', 'web_store_info','vendor_info','exchange_rate',
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
                    print e
            elif isinstance(value, float):
                value = str(value)
            elif isinstance(value, dict):
                value = str(value)
            item[key] = value


        self.companylist.append([item['title'], item['detail_url'], item['price'], item['original_price'], item['official_retail_price'], item['currency'],
                                item['sku'], item['product_id'], item['brand'], item['model'], item['material'], item['color'], item['size'], item['sex'],item['web_name'],
                                item['type'], item['subtype'], item['origin_condition'], item['photo_list'], item['sell_date'], item['sold_date'], item['crawl_date'],
                                item['standard_condition'], item['web_info'], item['web_store_info'],item['vendor_info'],item['exchange_rate'],item['full_content'],
                                 item['official_price'], item['condition_new_price']])
        # self.companylist.append([item['title'], item['sku']])
        if len(self.companylist) == 1000:
            self.bulk_insert_to_mysql(self.companylist)
            # 清空缓冲区
            del self.companylist[:]
        return item

    def close_spider(self, spider):
        print 'closing spider,last commit', len(self.companylist)
        self.bulk_insert_to_mysql(self.companylist)
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
