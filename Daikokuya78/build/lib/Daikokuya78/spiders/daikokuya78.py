# -*- coding: utf-8 -*-
import json
import requests
import re
import numpy as np
from scrapy.spidermiddlewares.httperror import HttpError

from Daikokuya78.items import *


class Daikokuya78Spider(scrapy.Spider):
    name = 'daikokuya78'
    allowed_domains = ['www.daikokuya78.com']
    # start_urls = ['http://www.daikokuya78.com/']
    # proxies = {'http': 'socks5://127.0.0.1:1080'}
    proxies = 'socks5://127.0.0.1:1080'
    exchange_rate_dict = {'USD': 1.0}
    all_dict = {}
    type_num = 0

    def start_requests(self):
        brand_num = [1, 3, 2, 8, 4, 7, 647, 88, 9, 541]
        for brand in brand_num:
            url = "https://www.daikokuya78.com/shop/goods/search.aspx?keyword=&name=&tree=10&min_price=1&max_price=&maker=%s&goods_code=&attr3=&sort=spd&search.x=105&search.y=22" %brand
            yield scrapy.Request(url, callback=self.parse_page, meta={'brand': brand})

    def parse_page(self, response):
        self.type_num += 1
        brand = response.meta['brand']
        print(brand)
        try:
            total = response.xpath("//div[@class='block_wrapper_']/p/text()").extract()[0].strip()
            print("total1====", total)
            total = int(re.findall(r"\d+", total)[-1])

        except Exception as e:
            total = 0
            print(e)
        print(type(total), total)
        if total == 0:
            pass
        if total >= 5000:
            max_price = response.xpath("//span[@class='price_']/text()").extract()[0]
            max_price = int(''.join(re.findall(r'\d+', max_price)))
            print(max_price)
            price_list = np.arange(1, max_price+100000, 100000)
            print(price_list)
            # for i in range(len(price_list)):
            for i in range(1):
                if i == len(price_list)-1:
                    break
                min_price = price_list[i]
                max_price = price_list[i+1]
                url = "https://www.daikokuya78.com/shop/goods/search.aspx?keyword=&name=&tree=10&min_price=%s&max_price=%s&maker=%s&goods_code=&attr3=&sort=spd&search.x=105&search.y=22"%(min_price, max_price, brand)
                yield scrapy.Request(url, callback=self.parse_page)
        else:
            if total % 28 != 0:
                page_num = total // 28 + 1
            else:
                page_num = total // 28
            for page in range(page_num):
            # for page in range(1):
                page_op = str(page + 1) + "_type" + str(self.type_num)
                page = page + 1
                print(page)
                url = response.url + '&p=' + str(page)
                print(url)
                yield scrapy.Request(url, callback=self.parse, meta={"op": page_op})

    def parse(self, response):
        page_op = response.meta['op']
        url_list = response.xpath("//div[@class='desc_']/a/@href").extract()
        product_num = len(url_list)
        for url in url_list:
            product_op = page_op + "_" + str(url_list.index(url) + 1) + str(product_num)
            url = "https://www.daikokuya78.com" + url
            yield scrapy.Request(url, callback=self.parse_html, meta={"op": product_op})
        # price = response.xpath("//div[@class='desc_']/a/span[@class='price_']").extract()
        # print("数量:", len(price))
        # print(response.url)

    def parse_html(self, response):
        item = Daikokuya78Item()
        item['detail_url'] = response.url
        item['product_id'] = response.xpath("//td[@id='spec_goods']/text()").extract()[0]
        item['currency'] = 'JPY'
        item['type'] = 'bag'
        item['web_name'] = 'daikokuya'
        item['sku'] = item['web_name'] + item['product_id']
        item['web_info'] = {"name": "daikokuya", "country": "Japan", "city": "Tokyo",
                            "address": "Rivage Shinagawa Bld.3F, 4-1-8 konan, Minato-ku, Tokyo, Japan",
                            "phone": "03-3472-7740", "language": "Japanese", "image_resolution": "640*480",
                            "location": {"longitude": "-74.006550", "Latitude": "40.751580"}, "currency": "JPY",
                            "business_type": "2"}
        # print("商品的ID:", item['product_id'])
        # if item['product_id']:
        #     item['title'] = response.xpath("//span[@class='txt_2_']").extract()[0]
        #     item['']
        #     status = response.xpath("//div[@class='cartbox_ top']/img/@alt").extract()[0]
        #     if status:
        #         item["status"] = status
        try:
            price = response.xpath("//p[@class='price1_']/span[@class='price_']/text()").extract()[0]
            item['price'] = re.findall(r'(\d+)', price.replace(',', ''))[0]
            print('价格', item['price'])
        except Exception as e:
            item['price'] = ''
            print(e)
        try:
            item['title'] = response.xpath(r"//span[@class='txt_2_']/text()").extract()[0]
            print('title', item['title'])
        except Exception as e:
            item['title'] = ''
            print(e)
        try:
            official_retail_price = response.xpath("//p[@class='price2_']/span[@class='price_']/text()").extract()[0]
            item['official_retail_price'] = re.findall(r'(\d+)', official_retail_price.replace(',', ''))[0]
        except Exception as e:
            item['official_retail_price'] = ''

        try:
            item['brand'] = response.xpath("//div[@class='box_brand_']/dl/dd/text()").extract()[0]
        except Exception as e:
            item['brand'] = ''

        try:
            item['material'] = response.xpath("//td[@id='spec_goods_name']/text()").extract()[-1]
        except Exception as e:
            item['material'] = ''

        try:
            item['color'] = response.xpath("//td[@id='spec_variation_name2']/text()").extract()[0]
        except Exception as e:
            item['color'] = ''
        sizeDict = {"depth": "", "width": "", "height": "", "handle": "", "drop": ""}
        try:
            size = response.xpath("//td[@id='spec_variation_name1']/text()").extract()[0]
            size = re.findall(r'[0-9]\d+\.\d+|\d+', size)
        except Exception as e:
            size = ''
        if size:
            sizeDict["width"] = size[0]
            try:
                sizeDict['height'] = size[1]
            except Exception as e:
                sizeDict['height'] = ''
            try:
                sizeDict['depth'] = size[2]
            except Exception as e:
                sizeDict['depth'] = ''
        item['size'] = sizeDict
        try:
            item['origin_condition'] = response.xpath("//td[@id='spec_attr3']/text()").extract()[0]
        except Exception as e:
            item['origin_condition'] = ''
        if item['origin_condition'].strip() == '新品（N）':
            item['condition_new_price'] = item['price']

        try:
            photo_list = list()
            imag_L = response.xpath("//div[@class='img_L_']/a/img/@src").extract()
            img_l = response.xpath("//div[@class='etc_goodsimg_']//div[@class='etc_goodsimg_item_']/p/a/img/@src").extract()
            image_list = imag_L+img_l
            for url in image_list:
                photo_url = "https://www.daikokuya78.com" + url + '#id=' + item['sku'] + '&v_' + str(image_list.index(url)+1)
                photo_list.append(photo_url)
            item['photo_list'] = photo_list
        except Exception as e:
            item['photo_list'] = ''

        try:
            item['subtype'] = response.xpath("//td[@id='spec_attr2']/text()").extract()[0]
        except Exception as e:
            item['subtype'] = ''

        if item['currency'] != "" or item['currency']:
            exchange_rate = self.exchange_rate_currency(item['currency'])
        else:
            exchange_rate = 1.0
        try:
            item['exchange_rate'] = exchange_rate
        except Exception as e:
            item['exchange_rate'] = '0.0'

        yield item

    def exchange_rate_currency(self, currency):
        if currency in self.exchange_rate_dict.keys():
            exchange_rate = self.exchange_rate_dict[currency]
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            }
            url = 'https://freecurrencyrates.com/api/action.php?s=fcr&iso=' + currency + '&f=USD&v=1&do=cvals&ln=zh-hans'
            res = requests.get(url, headers=headers)
            result = json.loads(res.text)
            exchange_rate = float(result[currency])
            self.exchange_rate_dict[currency] = exchange_rate
        return exchange_rate

    def all_dict_setting(self, page_num, product_num):
        self.all_dict[page_num] = {}
        type_num = re.findall('type(\d+)', page_num)[0]  # 获取type值
        page = re.findall('(\d+)_', page_num)[0]  # 获取当前页
        self.all_dict[page_num]['page_num'] = page
        self.all_dict[page_num]['product_num'] = product_num
        self.all_dict[page_num]['response_num'] = product_num
        self.all_dict[page_num]['left_num'] = 0
        self.all_dict[page_num]['left_url'] = {}
        self.all_dict[page_num]['status'] = 200
        self.all_dict[page_num]['type_num'] = type_num

    # 爬虫结束后自动调用
    def closed(self, spider):
        # browser.quit()
        with open(self.name + "_page_detail.json", "wb") as f:
            for i in sorted(self.all_dict):
                jsons = json.dumps(self.all_dict[i])
                f.write(jsons)
                f.write("\n")
                if self.all_dict[i]['status'] != 200:
                    with open(self.name + "_error_detail.json", "wb") as e:
                        e.write(jsons)
                        e.write("\n")

    def errback(self, failure):
        if failure.check(HttpError):
            # 保存错误信息
            count = ''
            response = failure.value.response
            page_op = response.meta['op']
            page_num = re.findall(r'(.+)_\d+', page_op)
            if page_num:
                page_num = page_num[0]
                count = re.findall(r'.+_(\d+)', page_op)[0]
                current_response_num = int(self.all_dict[page_num]['response_num']) - 1
                self.all_dict[page_num]['status'] = response.status
                self.all_dict[page_num]['response_num'] = current_response_num
                self.all_dict[page_num]['left_num'] += 1
                self.all_dict[page_num]['left_url'][response.url] = 1
                self.all_dict[page_num]['count'] = count  # 当前页第几个错误
            else:
                self.all_dict[page_op] = {}
                self.all_dict[page_op]['left_url'] = {}
                self.all_dict[page_op]['status'] = response.status
                self.all_dict[page_op]['left_url'][response.url] = 1










