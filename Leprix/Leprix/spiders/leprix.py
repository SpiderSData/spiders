# -*- coding: utf-8 -*-
import scrapy
from Leprix.items import LeprixItem
import pymysql
from Leprix.constant import brand_name
import re
import sys
from scrapy.spidermiddlewares.httperror import HttpError
import json
from geopy.geocoders import Nominatim
import urllib2
from geopy.exc import GeocoderTimedOut
import math
from requests.adapters import HTTPAdapter
import time
from decimal import *
import requests
from Leprix.settings import *


defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


times = time.strftime('%Y-%m-%d', time.localtime())
oneday = time.strftime('%Y-%m-%d', time.localtime(time.time()-86400*1))
twoday = time.strftime('%Y-%m-%d', time.localtime(time.time()-86400*2))
addressdict = {}
def get_all_data():
#    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='scrapys')
    conn = pymysql.connect(host=MYSQL_HOST,
                           port=MYSQL_PORT,
                           user=MYSQL_USER,
                           passwd=MYSQL_PWD,
                           db=MYSQL_DB)
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8mb4;')
    cursor.execute('SET CHARACTER SET utf8mb4;')
    cursor.execute('SET character_set_connection=utf8mb4;')

    item = [
        'product_id', 'title', 'price', 'original_price', 'official_retail_price', 'currency', 'sku',
        'brand', 'model', 'material', 'color', 'size', 'sex', 'type', 'subtype', 'origin_condition', 'photo_list',
        'sell_date', 'sold_date', 'crawl_date', 'web_info', 'web_store_info',
        'vendor_info', 'standard_condition', 'full_content'
    ]
    
    # sql_select = "select "+','.join(item)+" from AllData where web_name='"+brand_name.lower()+"' and product_id !='' "
    sql_select = "select "+','.join(item)+" from AllData where web_name='"+brand_name.lower()+"' and (crawl_date = '"+str(oneday)+"' or crawl_date='"+str(twoday)+"')"

    cursor.execute(sql_select)
    result = cursor.fetchall()

    conn.commit()
    conn.close()

    result_dict = {}
    for i in result:
        result_dict[i[0]] = i

    return result_dict

class LeprixSpider(scrapy.Spider):
    name = 'leprix'
    # allowed_domains = ['leprix.com']
    # all_data = get_all_data()

    page_num = 0  # 当前页码
    response_num = 0  # 当前请求成功页
    left_num = 0  # 当前请求错误页
    left_url = {}  # 请求错误url
    all_dict = {}  #存储所有json
    type_num = 0  #类型
    exchange_rate_dict = {"USD": 1.0}
    proxies = 'https://3.229.216.245:3306'  # , 'https': 'socks5://127.0.0.1:1080'
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': "__cfduid=d4ca0036f0bbefc7107db5de5024007e41562749202; _ga=GA1.2.1383095945.1562749208; tracker_device=f99cd697-26e8-46fd-afc6-8bfb35975395; oribi_user_guid=293ad6e0-fc3a-e21a-3a06-bd55185b4f7a; cto_lwid=17733953-309e-4da2-87da-46476278bc6d; _omappvp=hrJauHZsqZHzRO5zUNnnAHkEo4bqwStn7wGHoCtcp0Odt5pB2gbV8w9ab6MLHGf4ZY3eGc040vp1mWNXUbCghQxG0Grcwk7y; __ssid=d51892acdb823d7062ea7c6b168387f; rskxRunCookie=0; rCookie=s8o71pq46tk7zmexauz6kwjxx0lyfk; __zlcmid=tDiNJ5P7Rh0nBB; lastRskxRun=1562749598918; _hjid=9c632a6e-34ca-487a-8c11-750fab1d4564; _fbp=fb.1.1565346597255.1002485927; __stripe_mid=7f37c3c5-48b8-4795-959c-22cd4ec33675; _gid=GA1.2.94929240.1568874275; inside-psid=2019-09-19T06%3A24%3A47.3051694Z; inside-sexp=true; cf_clearance=10815857bbb13b83057a6d6ef0ffe22365582664-1568874453-1800-150; XSRF-TOKEN=eyJpdiI6IlR3MTQ4M052eUQrY00xbk5ZTThGNXc9PSIsInZhbHVlIjoiaFZqVVJoMzBnUFNzOWNqcjltR0xZaHdcL2FxYWdUOHlsRG8zb0pYTTRPbThPUTI2blp4Z1dCWEpMR09JOUZxbjQiLCJtYWMiOiIzZjk4YzUwOTdlYTI1NmQ3MGZkOGM4ZTY1ZDcyM2JmYzNjYTE0YmUwNjA3OTlkMzE4ZThhNjg4NTVjMzNkNDdmIn0%3D; leprix_session=eyJpdiI6Iit2K0pZZGZTeHpYTVg3M0tER1o0MWc9PSIsInZhbHVlIjoiNUpRYWxzSlNMNTQ0aFVkcjFqMWNYTXZLUFwvcEY5cVFtQmpPMFFOWkhXNWQ5SDB6YnJBa3M0YUk4NEh0cE9IMGEiLCJtYWMiOiJmODU5MWRhODNjMzdkYjZhNmY0YzFjMGMzMGY0MTFjYzBhYjY1MTU2ZDVjMDE5N2U1N2QyNzQwNGU0MWQ0NjliIn0%3D; _gat_UA-22708850-4=1; amplitude_id_4e1fc52d3ac5271d4242eb2156597d9eleprix.com=eyJkZXZpY2VJZCI6IjAwY2E0NGEyLTQwZTEtNDQ5Ni1iZTQ4LWJiOGUzYWMyM2MwMlIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTU2ODg3NDI3MzI5OCwibGFzdEV2ZW50VGltZSI6MTU2ODg3NDQ1NTEyNywiZXZlbnRJZCI6MjIsImlkZW50aWZ5SWQiOjAsInNlcXVlbmNlTnVtYmVyIjoyMn0=; mp_snobswap_mixpanel=%7B%22distinct_id%22%3A%20%2216c75ed7f723a1-0460f8f1f0e42d-3f75065b-1fa400-16c75ed7f73df0%22%2C%22bc_persist_updated%22%3A%201565346594677%7D; inside-us=357157769-6b1adc4810dd98fffde9f69392a412cb67f6fe8ef0d91ebb5684381e9ccdeaeb-5-5",

    }

    def start_requests(self):

        start_urls = [
            "https://leprix.com/shop/women/handbags?pp=40&s=inexpensive&price=2%3A1%3A0%3A3&timestamp=1534297752594",
            "https://leprix.com/shop/women/handbags?pp=40&s=inexpensive&price=4%3A5&timestamp=1534297792103",
            "https://leprix.com/shop/women/handbags?pp=40&s=inexpensive&price=6%3A7%3A8&timestamp=1534297867108"
        ]
        for url in start_urls:
            print("进来")
            yield scrapy.Request(url, callback=self.parse_page, headers=self.headers, dont_filter=True, meta={'proxy': self.proxies})  # , 'proxy': self.proxies

    def parse_page(self, response):
        print("代理成功！")
#         url = response.url
#         url1 = 'https://leprix.com/shop/women/handbags?pp=40&s=inexpensive'
#         url2 = re.findall(r'&price.*', url)[0]
#         number = response.xpath("//div[@class='row align-items-center mb-3 mt-5']/div[1]/text()").extract()[0]
#         number = re.findall(r'of\n(.*) item', number)
#         number = ''.join(number).replace(',', '')
#         number = int(math.ceil(float(number) / 40))+1
#
#         self.type_num += 1  # start_urls来递加类型
#         # for i in range(1, number):
#
#
#         for i in range(1, number):
#             url = url1 + '&p=' + str(i) + url2
#             page_op = str(i) + "_type" + str(self.type_num)  # 返回页数、类型
#             print("---------")
#             print(url)
#             yield scrapy.Request(url, callback=self.parse, headers=self.headers,
#                                  errback=self.errback, meta={"op": page_op,
#                                                              'dont_redirect': True,
#                                                              'proxy': self.proxies})
#
#     def parse(self, response):
#         page_op = response.meta['op']
#         url_list = response.xpath("//div[@id='results']/div/a/@href").extract()
#         productlist = response.xpath("//div[@id='results']/div/@id").extract()
#         item = LeprixItem()
#         if len(url_list)==0:
#             print("error--------------------------")
#             print(response.url)
#
#             scrapy.Request(response.url, callback=self.parse_detail_page, headers=self.headers, errback=self.errback)
#             print("停止")
#             return
#         product_num = len(url_list)
#         self.all_dict_setting(page_op, product_num)
#
#         for urls in range(int(product_num)):
#             url = url_list[urls].encode("utf-8")
#             product_op = page_op + "_" + str(urls + 1)
#             try:
#                 productid = productlist[urls]
#                 print("product-id-------------------------------------")
#                 print(productid)
#                 item['product_id'] = productid
#                 item['currency'] = 'USD'
#             except Exception as e:
#                 print e
#
#             if item['currency'] != "" or item['currency']:
#                 if item['currency'] in self.exchange_rate_dict.keys():
#                     exchange_rate = self.exchange_rate_dict[item['currency']]
#                 else:
#                     currencyurl = 'https://freecurrencyrates.com/api/action.php?s=fcr&iso=' + item[
#                         'currency'] + '&f=USD&v=1&do=cvals&ln=zh-hans'
#                     s = requests.Session()
#                     s.mount('http://', HTTPAdapter(max_retries=3))
#                     s.mount('https://', HTTPAdapter(max_retries=3))
#                     r = s.get(currencyurl, timeout=3)
#                     result = json.loads(r.text)
#                     exchange_rate = float(result[item['currency']])
#                     self.exchange_rate_dict[item['currency']] = exchange_rate
#             else:
#                 exchange_rate = 1.0
#             try:
#                 item['exchange_rate'] = exchange_rate
#             except Exception as e:
#                 print e
#
#             # 判断数据库中是否存在该product_id
#             # if item['product_id'] in self.all_data.keys():
#             #     print("在数据库中")
#             #     # 用数据库信息补全
#             #     pro_data = self.all_data[item['product_id']]
#             #     item['title'] = pro_data[1]
#             #     try:
#             #         prices = response.xpath(
#             #             "//div[@id='" + item['product_id'] + "']//p[contains(@class,'product-price')]/text()").extract()
#             #         if len(prices) >= 3:
#             #             price = prices[1].replace("was", "").replace(",","").replace("$", "").strip()
#             #             item['price'] = "%.2f" % float(
#             #                         ''.join(re.findall(r'\d+\.*\d*', price)))
#             #             for i in prices:
#             #                 if re.search("was", i):
#             #                     original_price = i.replace("was", "").replace(",", "").replace("$", "").strip()
#             #                     item['original_price'] = "%.2f" % float(
#             #                         ''.join(re.findall(r'\d+\.*\d*', original_price)))
#             #
#             #                 if re.search("ret", i):
#             #                     official_retail_price = i.replace("est.", "").replace("ret.", "").replace("$",
#             #                                                                                               "").replace(
#             #                         ",", "").strip()
#             #                     item['official_retail_price'] = "%.2f" % float(
#             #                         ''.join(re.findall(r'\d+\.*\d*', official_retail_price)))
#             #         elif len(prices) >= 2:
#             #             item['original_price'] = pro_data[3]
#             #             item['official_retail_price'] = pro_data[4]
#             #             price = prices[1].replace("was", "").replace(",","").replace("$", "").strip()
#             #             item['price'] = "%.2f" % float(
#             #                         ''.join(re.findall(r'\d+\.*\d*', price)))
#             #     except Exception as e:
#             #         print e
#             #     item['sku'] = pro_data[6]
#             #     item['brand'] = pro_data[7]
#             #     item['model'] = pro_data[8]
#             #     item['material'] = pro_data[9]
#             #     item['color'] = pro_data[10]
#             #     item['size'] = pro_data[11]
#             #     item['sex'] = pro_data[12]
#             #     item['type'] = pro_data[13]
#             #     item['subtype'] = pro_data[14]
#             #     item['origin_condition'] = pro_data[15]
#             #     item['photo_list'] = pro_data[16].split(",")
#             #     item['sell_date'] = pro_data[17]
#             #     item['sold_date'] = pro_data[18]
#             #     item['crawl_date'] = times
#             #     item['web_name'] = 'LePrix'
#             #     item['web_info'] = pro_data[20]
#             #     item['web_store_info'] = pro_data[21]
#             #     item['web_info'] = str({"name": "LePrix", "country": "USA", "city": "Arlington, Virginia",
#             #                         "address": u"2231 Crystal Dr, Arlington, Virginia 22202, US",
#             #                         "phone": "18887470969", "language": "English",
#             #                         "image_resolution": "1920*1080",
#             #                         "location": {"longitude": "-77.04876", "latitude": "38.85377"}})
#             #     item['standard_condition'] = pro_data[23]
#             #     item['full_content'] = pro_data[24]
#             #     item['detail_url'] = url
#             #     yield item
#             # else:
#
#             yield scrapy.Request(url, callback=self.parse_detail_page, headers=self.headers, errback=self.errback, meta={"op": product_op, 'proxy': self.proxies})
#
#     def parse_detail_page(self, response):
#     # def parse_page(self, response):
#         item = LeprixItem()
#         s = response.body
#
#         try:
#             detail_url = response.url
#             item['detail_url'] = detail_url
#         except Exception as e:
#             print e
#
#         try:
#             title = response.xpath('//div[@class="mb-2"]/h1/text()').extract()
#             title = ''.join(title)
#             if title:
#                 item['title'] = title
#             else:
#                 item['title'] = []
#         except Exception as e:
#             print e
#         try:
#             brand = response.xpath("//div[@class='col-sm-12 col-md-5 item-details']/span[1]/a/p/text()").extract()
#             if brand:
#                 brand = ''.join(brand).encode('utf-8').replace('è', 'e')
#                 item['brand'] = brand
#             else:
#                 item['brand'] = []
#         except Exception as e:
#             print("brand error")
#             print e
#
#         try:
#             model = response.xpath("//div[@class='col-sm-12 col-md-5 item-details']/h1/text()").extract()
#             if model:
#                 model = ''.join(model)
#                 model = model.encode('utf-8')
#                 item['model'] = model
#             else:
#                 item['model'] = []
#         except Exception as e:
#             print("model error")
#             print e
#
#         prices = response.xpath("//h5[@class='text-muted-light']/text()").extract()
#         try:
#             # if prices:
#             #     original_price = prices.replace("was", "").replace(",", "").replace("$", "").strip()
#             #     item['original_price'] = "%.2f" % float(''.join(re.findall(r'\d+\.*\d*', original_price)))
#             if prices:
#                 for i in prices:
#                     if re.search("was", i):
#                         original_price = i.replace("was", "").replace(",", "").replace("$", "").strip()
#                         item['original_price'] = "%.2f" % float(''.join(re.findall(r'\d+\.*\d*', original_price)))
#
#                     elif re.search("ret", i):
#                         official_retail_price = i.replace("est.", "").replace("ret.", "").replace("$", "").replace(
#                             ",", "").strip()
#                         item['official_retail_price'] = "%.2f" % float(''.join(re.findall(r'\d+\.*\d*', official_retail_price)))
#         except Exception as e:
#             print("original_price error")
#             print e
#
#         try:
#             price = response.xpath("//h5[@class='price mb-0']/span[3]/text()").extract()
#             if price:
#                 price = ''.join(price).replace('$', '').replace('\n', '')
#                 price = "%.2f" % float(''.join(re.findall(r'\d+\.*\d*', price)))
#                 item['price'] = price.encode('utf8')
#             else:
#                 item['price'] = ''
#         except Exception as e:
#             print("price error")
#             print e
#
#             try:
#                 # case1 = re.findall(r'<br>BAG MEASURES:<br>(.{0,200})" <br>', s)
#                 # case2 = re.findall(r'<p>Measurements: .{0,200}"</p>', s)
#                 # case3 = re.findall(r'Measurements: (.{0,150})</p', s)
#                 # case4 = re.findall(r'MEASURES:<br>(LENGTH .{0,200})"<br>', s)
#                 description = ''.join(response.xpath('//article[@itemprop="description"]/div/p').xpath(
#                     'string(.)').extract()).lower().replace(u'\u2033', '"').replace('\n', '')
#                 description2 = ''.join(response.xpath('//article[@itemprop="description"]/div').xpath(
#                     'string(.)').extract()).lower().replace(u'\u2033', '"').replace('\n', '')
#
#                 size_1 = ''.join(re.findall(r'Meas \(L" x W" x H"\): (.{0,20})\n', description, re.I))
#                 size_2 = ''.join(re.findall(r'Meas \(L" x W" x H"\): (.{0,20})\n', description2, re.I))
#
#                 #   depth 判断 des
#                 if re.findall(r'd (.{0,5}) x', description):
#                     width_length = ''.join(re.findall(r'w (.{0,5}) x', description))
#                     depth_width = ''.join(re.findall(r'd (\d+\.\d+|\d+)', description))
#                     height = ''.join(re.findall(r'h (.{0,5}) x', description))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?cm', description, re.I)):
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+)"', description, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+)"', description, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+)"', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+)"', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?in', description, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'(\d+\.\d+|\d+).*?depth', description, re.I)):
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)? width', description))
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)? depth', description))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)? height', description))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#
#
#                 #   length 判断 des
#                 elif re.findall(r'(\d+\.\d+|\d+)l', description):
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)l', description))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)h', description))
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)d', description))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#
#                 elif re.findall(r'l (.{0,5}) x', description):
#                     width_length = ''.join(re.findall(r'l (.{0,5}) x', description))
#                     depth_width = ''.join(re.findall(r'w (\d+\.\d+|\d+)', description))
#                     height = ''.join(re.findall(r'h (.{0,5}) x', description))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?cm', description, re.I)):
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?cm', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+)"', description, re.I)):  # 英寸
#                     strap_length = ''.join(re.findall(r'strap length.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     handle_length = ''.join(re.findall(r'handle length.*?(\d+\.\d+|\d+)', description2, re.I))
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+)"', description, re.I)).replace(
#                         handle_length, '').replace(strap_length, '')
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+)"', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+)"', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?in', description, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?in', description, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'(\d+\.\d+|\d+).*?length', description, re.I)):
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)? length', description))
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)? width', description))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)? height', description))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#
#                 #   depth 判断 des2
#                 elif re.findall(r'd (.{0,5}) x', description2):
#                     width_length = ''.join(re.findall(r'w (.{0,5}) x', description2))
#                     depth_width = ''.join(re.findall(r'd (\d+\.\d+|\d+)', description2))
#                     height = ''.join(re.findall(r'h (.{0,5}) x', description2))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?cm', description2, re.I)):
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?cm', description2, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?cm', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?cm', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+)"', description2, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?in', description2, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     depth_width = ''.join(re.findall(r'depth.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'(\d+\.\d+|\d+).*?depth', description, re.I)):
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)? width', description2))
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)? depth', description2))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)? height', description2))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#
#                 #   length 判断 des2
#                 elif re.findall(r'(\d+\.\d+|\d+)l', description2):
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)l', description2))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)h', description2))
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)d', description2))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif re.findall(r'l (.{0,5}) x', description2):
#                     width_length = ''.join(re.findall(r'l (.{0,5}) x', description2))
#                     depth_width = ''.join(re.findall(r'w (\d+\.\d+|\d+)', description2))
#                     height = ''.join(re.findall(r'h (.{0,5}) x', description2))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?cm', description2, re.I)):
#                     no_need = ''.join(re.findall(r'length \(unzipped\) (.{0,3})cm', description2))
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?cm', description2, re.I)).replace(
#                         no_need, '')
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?cm', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?cm', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+)"', description2, re.I)):  # 英寸
#                     strap_length = ''.join(re.findall(r'strap length.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     handle_length = ''.join(re.findall(r'handle length.*?(\d+\.\d+|\d+)', description2, re.I))
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+)"', description2, re.I)).replace(
#                         handle_length, '').replace(strap_length, '')
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+)"', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?in', description2, re.I)):  # 英寸
#                     width_length = ''.join(re.findall(r'length.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     depth_width = ''.join(re.findall(r'width.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     height = ''.join(re.findall(r'height.*?(\d+\.\d+|\d+).*?in', description2, re.I))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif ''.join(re.findall(r'(\d+\.\d+|\d+).*?length', description2, re.I)):
#                     width_length = ''.join(re.findall(r'(\d+\.\d+|\d+)? length', description2))
#                     depth_width = ''.join(re.findall(r'(\d+\.\d+|\d+)? width', description2))
#                     height = ''.join(re.findall(r'(\d+\.\d+|\d+)? height', description2))
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#
#                 elif size_1:
#                     width_length = re.findall(r'\d+\.\d+|\d+', size_1)[0]
#                     depth_width = re.findall(r'\d+\.\d+|\d+', size_1)[1]
#                     height = re.findall(r'\d+\.\d+|\d+', size_1)[2]
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 elif size_2:
#                     width_length = re.findall(r'\d+\.\d+|\d+', size_2)[0]
#                     depth_width = re.findall(r'\d+\.\d+|\d+', size_2)[1]
#                     height = re.findall(r'\d+\.\d+|\d+', size_2)[2]
#                     item['size'] = 'Height: ' + height + ' Length: ' + width_length + ' Width: ' + depth_width
#                 else:
#                     size_3 = re.search(r'\d.{0,5}w|\d.{0,5}" w|\d.{0,5}"w', description).group().replace('" w',
#                                                                                                          '').replace(
#                         'w', '').replace('"w', '')
#                     size_4 = re.search(r'\d.{0,5}w|\d.{0,5}" w|\d.{0,5}"w', description2).group().replace('" w',
#                                                                                                           '').replace(
#                         'w', '').replace('"w', '')
#
#                     if size_3:
#                         item['size'] = 'width: ' + ''.join(size_3)
#                     elif size_4:
#                         item['size'] = 'width: ' + ''.join(size_4)
#
#
#             except Exception as e:
#                 print("size error")
#                 print e
#
#         try:
#             subtype = response.xpath('//ol[@class="breadcrumb"]/li[4]/a/text()').extract()
#             if subtype:
#                 item['subtype'] = ''.join(subtype).replace(" Bags","")
#             else:
#                 item['subtype'] = []
#         except Exception as e:
#             print e
#
#         item['type'] = 'bag'
#
#         try:
#             sex = response.xpath('//ol[@class="breadcrumb"]/li[2]/a/text()').extract()
#             if sex:
#                 item['sex'] = ''.join(sex)
#             else:
#                 item['sex'] = []
#         except Exception as e:
#             print("sex error")
#             print e
#
#         try:
#             material = re.findall(r'<td>\nMaterial: </td>\n.*\n(.*)', s)
#             if material:
#                 material = ''.join(material).replace('</tr>', '').replace('</td>', '').replace('</table>', '').replace('</div>', '')
#                 item['material'] = material
#             else:
#                 mt_list = [u"chevre mysore", u"lambskin leather", u"vache leather", u"vache liegee leather",
#                            u"vache trekking leather", u"snake print",
#                            u"vibrato leather", u"grained leather", u"patent leather", u"sombrero leather", u"crocodile leather",
#                            u"alligator leather", u"matt niloticus crocodile skin", u"matt porosus crocodile skin",
#                            u"niloticus crocodile skin", u"porosus crocodile skin", u"alligator crocodile skin",
#                            u"matt alligator", u"veau leather", u"veau tadelakt leather", u"ostrich leather", u"sikkim leather",
#                            u"velvet leather", u"taurillon cristobal", u"ardennes leather", u"evergrain leather",
#                            u"box calf leather", u"python leather", u"lainage leather", u"nappa leather", u"calf leather",
#                            u"calfskin", u"grain d'h calfskin", u"barenia leather", u"barenia natural", u"clemence leather",
#                            u"courchevel leather", u"chevre leather", u"chevre myzore goatskin", u"chevre coromandel goatskin",
#                            u"derma leather", u"grizzly leather", u"troika leather", u"swift leather", u"peau porc", u"fjord leather",
#                            u"buffalo leather", u"buffalo sindhu leather", u"buffalo gala leather", u"buffalo pondichery leather",
#                            u"negonda leather", u"togo leather", u"chamonix leather", u"epsom leather", u"evercalf leather",
#                            u"graine leather", u"graine couchevel leather", u"graine lisse leather", u"lizard skin",
#                            u"lizard leather", u"natural lizard skin", u"amazonia leather", u"country leather", u"box leather",
#                            u"toile", u"toile h", u"toile gm", u"toile officier", u"toile so h", u"toile jean", u"toile chevrons",
#                            u"fabric", u"toile", u"toile h", u"toile gm", u"toile officier", u"toile so h", u"toile jean",
#                            u"toile chevrons", u"cloth", u"crinoline", u"denim", u"canvas", u"nylon canvas", u"monogram canvas",
#                            u"monogram fascination", u"monogram multicolor", u"chevrecoated canvas", u"plastic", u"satin",
#                            u"stainless steel", u"woven raffia", u"feathers", u"pvc", u"polyurethane", u"jute", u"velour", u"metal",
#                            u"felt", u"feutre", u"wicker", u"clear vinyl", u"textile", u"crystals", u"rubber", u"tpm", u"graphite",
#                            u"polyester", u"cotton", u"suede", u"silk", u"plexiglass", u"tessuto", u"nylon", u"lambskin", u"crocodile",
#                            u"python skin", u"python", u"velvet", u"croc", u"embossed", u"leather"]
#                 material_title = ''.join(response.xpath('//div[@class="mb-2"]/h1/text()').extract()).lower()
#                 description = ''.join(response.xpath('//article[@itemprop="description"]/div/p').xpath('string(.)').extract())
#                 description2 = ''.join(response.xpath('//article[@itemprop="description"]/div').xpath('string(.)').extract())
#                 for i in mt_list:
#                     if i in material_title.lower():
#                         item['material'] = i
#                     elif i in description.lower():
#                         item['material'] = i
#                     elif i in description2.lower():
#                         item['material'] = i
#         except Exception as e:
#             print("material error")
#             print e
#         item['currency'] = 'USD'
#
#         if item['currency'] != "" or item['currency']:
#             if item['currency'] in self.exchange_rate_dict.keys():
#                 exchange_rate = self.exchange_rate_dict[item['currency']]
#             else:
#                 currencyurl = 'https://freecurrencyrates.com/api/action.php?s=fcr&iso=' + item[
#                     'currency'] + '&f=USD&v=1&do=cvals&ln=zh-hans'
#                 s = requests.Session()
#                 s.mount('http://', HTTPAdapter(max_retries=3))
#                 s.mount('https://', HTTPAdapter(max_retries=3))
#                 r = s.get(currencyurl, timeout=3)
#                 result = json.loads(r.text)
#                 exchange_rate = float(result[item['currency']])
#                 self.exchange_rate_dict[item['currency']] = exchange_rate
#         else:
#             exchange_rate = 1.0
#         try:
#             item['exchange_rate'] = exchange_rate
#         except Exception as e:
#             print e
#
#         item['vendor_info'] = {"name": "", "country": "", "city": "", "address": "", "page": "", "phone": "",
#                                "word": "",
#                                "store": "", "location": {"longitude": "", "latitude": ""}}
#
#         try:
#             description = ''.join(response.xpath('//article[@itemprop="description"]/div/p').xpath('string(.)').extract()).lower().replace(u'\u2033', '"').replace('\n', ' ')
#             description2 = ''.join(response.xpath('//article[@itemprop="description"]/div').xpath('string(.)').extract()).lower().replace(u'\u2033', '"').replace('\n', ' ')
#             if description:
#                 item['vendor_info']['word'] = description.replace('"', '').replace('#', '').replace('\n', '')\
#                     .replace('\r', '').replace('\t', '').replace("estimated"," estimated")\
#                     .replace("condition"," condition").replace("measurements"," measurements").replace("accessories"," accessories")\
#                     .replace("designer", " designer").replace("model"," model").replace("item number"," item number")
#             elif description2:
#                 item['vendor_info']['word'] = description2.replace('"', '').replace('#', '').replace('\n', '').replace('\r', '').replace('\t', '').replace("estimated"," estimated")\
#                     .replace("condition"," condition").replace("measurements"," measurements").replace("accessories"," accessories")\
#                     .replace("designer", " designer").replace("model"," model").replace("item number"," item number")
#             address = response.xpath('//div[@class="row mb-3"]/div/p[2]/text()').extract()
#             if address:
#                 address = ''.join(address)
#                 item['vendor_info']['city'] = address
#             else:
#                 item['vendor_info']['city'] = ""
#             vendor_name = response.xpath('//div[@class="row mb-3"]/div/p/strong/text()').extract()
#             if vendor_name:
#                 item['vendor_info']['name'] = ''.join(vendor_name)
#             else:
#
#                 item['vendor_info']['name'] = ""
#             page = response.xpath('//div[@class="col-xl-9"]/div/div[1]/a/@href').extract()
#             if page:
#                 item['vendor_info']['page'] = ''.join(page)
#             else:
#                 item['vendor_info']['page'] = ""
#             item['vendor_info']['phone'] = '18887470969'
#         except Exception as e:
#             print("vendor_info error")
#             print e
#
#
#         address = response.xpath('//div[@class="row mb-3"]/div/p[2]/text()').extract()
#         address = ''.join(address)
#         if address:
#             if addressdict.has_key(address):
#
#                 item['vendor_info']['country'] = addressdict[address]['country']
#                 item['vendor_info']['location']['longitude'] = addressdict[address]['lon']
#                 item['vendor_info']['location']['latitude'] = addressdict[address]['lat']
#                 item['vendor_info']['address'] = addressdict[address]['address']
#             else:
#
#                 url = 'https://nominatim.openstreetmap.org/search?q=' + address + '&limit=1&format=json'
#                 if url:
#                     url = url.replace(' ', '%20').replace(',', '')
#                     c = urllib2.urlopen(url)
#                     d = c.read()
#                     result = json.loads(d)
#                     if result:
#                         addressdict[address] = {}
#                         country = ''.join(re.findall(r', (\w+)$', result[0]['display_name']))
#                         if u'Dubai' in address:
#                             result[0]['display_name'] = u'Dubai, Al Khamla Street, Emirates Hills, Dubai, Dubai, 24857, UAE'
#                         addressdict[address] = dict(country = country,lon = result[0]['lon'],lat = result[0]['lat'],address=result[0]['display_name'])
#                         item['vendor_info']['country'] = addressdict[address]['country']
#                         item['vendor_info']['location']['longitude'] = addressdict[address]['lon']
#                         item['vendor_info']['location']['latitude'] = addressdict[address]['lat']
#                         item['vendor_info']['address'] = addressdict[address]['address']
#                     # elif address:
#                     #     address = ''.join(address)
#                     #     geolocator = Nominatim()
#                     #     location = geolocator.geocode(address)
#                     #     if location.address == re.findall(r'\w+', location.address):
#                     #         geolocator = Nominatim()
#                     #         location = geolocator.geocode(address)
#                     #         if u'Dubai' in address:
#                     #             location.address = u'Dubai, Al Khamla Street, Emirates Hills, Dubai, Dubai, 24857, UAE'
#                     #             item['vendor_info']['country'] = ''.join(re.findall(r', (\w+)$', location.address))
#                     #             item['vendor_info']['location']['longitude'] = location.longitude
#                     #             item['vendor_info']['location']['latitude'] = location.latitude
#                     #             item['vendor_info']['address'] = location.address.encode('utf-8')
#                     #         else:
#                     #             item['vendor_info']['country'] = ''.join(re.findall(r', (\w+)$', location.address))
#                     #             item['vendor_info']['location']['longitude'] = location.longitude
#                     #             item['vendor_info']['location']['latitude'] = location.latitude
#                     #             item['vendor_info']['address'] = location.address.encode('utf-8')
#
#
#         try:
#             color1 = re.findall(r'<label for="ac-2" class="dd">Color</label>\n<article class="pb-0">\n<p>(.{0,20})</p>', s)
#             color = response.xpath("//div[@class='description']/section/div[2]/article/p/text()").extract()
#             if color1:
#                 color1 = ''.join(color1).encode('utf-8')
#                 item['color'] = color1
#             elif color:
#                 if u"One Size" in color:
#                    item['color'] = []
#                 else:
#                   item['color'] = color
#             else:
#                 item['color'] = []
#         except Exception as e:
#             print("color error")
#             print e
#
#         try:
#             #product_id = re.findall(r'Item Number</strong>: (\d+)<', s)
#             product_id = response.xpath("//input[@id='messageModalItem']/@value").extract()
#             if product_id:
#                 product_id = ''.join(product_id).encode('utf-8')
#                 item['product_id'] = product_id
#             else:
#                 item['product_id'] = ''
#         except Exception as e:
#             print e
#
#         try:
#             condit = response.xpath('//div[@class="description"]/section/div[4]/article[1]/p[1]/text()').extract()
#             condit = ''.join(condit)
#             condition = re.findall(r'(.*) \(', condit)
#             if condition:
#                 condition = ''.join(condition).encode('utf8')
#                 item['origin_condition'] = condition
#                 if "New" in condition:
#                     item['standard_condition'] = '10'
#                 elif "Like New" in condition:
#                     item['standard_condition'] = '9.9'
#                 elif "Gently Loved" in condition:
#                     item['standard_condition'] = '9'
#                 elif "Well Worn" in condition:
#                     item['standard_condition'] = '8'
#             else:
#                 item['standard_condition'] = []
#         except Exception as e:
#             print("condition error")
#             print e
#
#         print("product_______________________")
#         print(response.url)
#         print(item['product_id'])
#
#         item['sku'] = 'leprix' + item['product_id']
#         try:
#             photo_list = []
#             case1 = re.findall(r'<img class="mx-auto d-block img-fluid white-block" src="(.{0,300})" data-original', s)
#             case2 = re.findall(r'<img class="card-img-top" src="(.{0,150}.jpg)', s)
#             case3 = response.xpath("//img[@id='mainImage']/@src").extract()
#             case4 = response.xpath("//a[@id='mainImageLink']/@href").extract()
#             if case1:
#                 for photo in case1:
#                     newphoto = photo + '#id=' + item['sku'] + '&v_' + str(case1.index(photo) + 1)
#                     newphoto = newphoto.replace('w=150', 'w=1920').replace('h=150', 'h=1080')
#                     photo_list.append(newphoto)
#                 item['photo_list'] = photo_list
#             elif case2:
#                 for photo in case2:
#                     newphoto = photo + '#id=' + item['sku'] + '&v_' + str(case2.index(photo) + 1)
#                     newphoto = newphoto.replace('w=150', 'w=1920').replace('h=150', 'h=1080')
#                     photo_list.append(newphoto)
#                 item['photo_list'] = photo_list
#             elif case3:
#                 for photo in case3:
#                     newphoto = photo + '#id=' + item['sku'] + '&v_' + str(case3.index(photo) + 1)
#                     newphoto = newphoto.replace('w=150', 'w=1920').replace('h=150', 'h=1080')
#                     photo_list.append(newphoto)
#                 item['photo_list'] = photo_list
#             elif case4:
#                 for photo in case4:
#                     newphoto = photo + '#id=' + item['sku'] + '&v_' + str(case4.index(photo) + 1)
#                     newphoto = newphoto.replace('w=150', 'w=1920').replace('h=150', 'h=1080')
#                     photo_list.append(newphoto)
#                 item['photo_list'] = photo_list
#         except Exception as e:
#             print("photo_error")
#             print e
#
#         item['crawl_date'] = times
#
#         item['web_name'] = 'LePrix'
#         item['web_info'] = {"name": "LePrix","country": "USA", "city": "Arlington, Virginia",
#                             "address": u"2231 Crystal Dr, Arlington, Virginia 22202, US",
#                             "phone": "18887470969", "language": "English",
#                             "image_resolution": "1920*1080",
#                             "location": {"longitude": "-77.04876", "latitude": "38.85377"}}
#         if item['standard_condition'] == '10':
#             try:
#                 item['condition_new_price'] = item['price']
#             except Exception as e:
#                 item['condition_new_price'] = ''
#                 print e
#
#         yield item
#
# # ----------------------------------------------------------=====================================-=-=-=-=
#
#
#         #
#         # try:
#         #     case1 = response.xpath("//p[@class='mb-3']/a/text()").extract()
#         #     case2 = response.xpath("//div[@class='col-sm-12 col-md-5 item-details']/div[4]/div/p[3]/a/text()").extract()
#         #     case1 = ''.join(case1)
#         #     case2 = ''.join(case2)
#         #     if case1:
#         #         case1 = ''.join(case1)
#         #         case1 = case1.encode('utf-8')
#         #         item['vendor_phone'] = case1
#         #     elif case2:
#         #         case2 = ''.join(case2)
#         #         case2 = case2.encode('utf-8')
#         #         item['vendor_phone'] = case2
#         #     else:
#         #         item['vendor_phone'] = []
#         # except Exception as e:
#         #     print e
#
#         # try:
#         #     descript = re.findall(r'<article itemprop="description" class="pb-0">\n(.{0,1000})</p>', s)
#         #     if descript:
#         #         for description in descript:
#         #             item['description'] = description
#         #     else:
#         #         item['description'] = []
#         # except Exception as e:
#         #     print e
#
#
#
#     def all_dict_setting(self, page_num, product_num):
#         self.all_dict[page_num] = {}
#         type_num  = re.findall(r'type(\d+)', page_num)[0]  # 获取type值
#         page  = re.findall(r"(\d+)_", page_num)[0]  # 获取当前页
#         self.all_dict[page_num]['page_num'] = page
#         self.all_dict[page_num]['product_num'] = product_num
#         self.all_dict[page_num]['response_num'] = product_num
#         self.all_dict[page_num]['left_num'] = 0
#         self.all_dict[page_num]['left_url'] = {}
#         self.all_dict[page_num]['status'] = 200
#         self.all_dict[page_num]['type_num'] = type_num
#     # 爬虫结束后自动调用
#
#     def closed(self, spider):
#         with open(self.name+"_page_detail.json", "wb") as f:
#             for i in sorted(self.all_dict):
#                 jsons = json.dumps(self.all_dict[i])
#                 f.write(jsons)
#                 f.write("\n")
#                 if self.all_dict[i]['status'] != 200:
#                     with open(self.name+"_error_detail.json","wb") as e:
#                         e.write(jsons)
#                         e.write("\n")
#
#                 # print("jsons")
#
#     def errback(self, failure):
#         if failure.check(HttpError):
#             count = ""
#             #保存错误信息
#             response = failure.value.response
#             page_op = response.meta['op']
#             page_num = re.findall('(.+)_\d+', page_op)
#             if page_num:
#                 page_num = page_num[0]
#                 count = re.findall('.+_(\d+)', page_op)[0]
#                 current_response_num = int(self.all_dict[page_num]['response_num']) - 1
#                 self.all_dict[page_num]['status'] = response.status
#                 self.all_dict[page_num]['response_num'] = current_response_num
#                 self.all_dict[page_num]['left_num'] += 1
#                 self.all_dict[page_num]['left_url'][response.url] = 1
#                 self.all_dict[page_num]['count'] = count  # 当前页第几个错误
#             else:
#                 self.all_dict[page_op] = {}
#                 self.all_dict[page_op]['left_url'] = {}
#                 self.all_dict[page_op]['status'] = response.status
#                 self.all_dict[page_op]['left_url'][response.url] = 1
