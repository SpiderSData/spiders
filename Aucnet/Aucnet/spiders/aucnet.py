# -*- coding: utf-8 -*-
import hashlib
import json
import sys
import pymysql
import requests
import scrapy
import time
import re
from scrapy.spidermiddlewares.httperror import HttpError
from selenium import webdriver
from Aucnet.settings import *
from Aucnet.items import AucnetItem



class AucnetSpider(scrapy.Spider):
    name = 'aucnet'
    # allowed_domains = ['www.brand-auc.com']
    # start_urls = ['http://www.brand-auc.com/login']
    times = time.strftime('%Y-%m-%d', time.localtime())
    page_num = 0  # 当前页码
    response_num = 0  # 当前请求成功
    left_num = 0  # 当前请求错误页
    left_url = {}  # 请求的错误ＵＲＬ
    all_dict = {}  # 存储所有json
    type_num = 0
    exchange_rate_dict = {"USD": 1.0}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
    }

    def start_requests(self):
        url = "https://www.aucmarketplace.com/share/login.php"

        yield scrapy.Request(url, callback=self.login)

    def login(self, response):
        url1 = response.url
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')

        driver = webdriver.Chrome(chrome_options=options)

        driver.get("https://www.aucmarketplace.com/share/login.php")

        time.sleep(3)
        # 用户名\发送
        uname = driver.find_element_by_name("login_email")
        uname.send_keys("K810113")

        # 密码\发送
        pwd = driver.find_element_by_name("login_pass")
        pwd.send_keys("184805696772")

        # 点击登录按钮

        driver.find_element_by_id("login_btn").click()
        # 解决报错unexpected alert open
        driver.switch_to.alert.accept()
        time.sleep(3)

        url2 = driver.current_url

        if url1 != url2:
            cookie = driver.get_cookies()
            print(cookie)
            cookie = {
                cookie[0]['name']: cookie[0]['value'],
                cookie[1]['name']: cookie[1]['value'],
                cookie[2]['name']: cookie[2]['value'],
                cookie[3]['name']: cookie[3]['value'],
                cookie[4]['name']: cookie[4]['value'],
            }
            print("提取后的cookie", cookie)
            driver.quit()

            url = "https://www.aucmarketplace.com/products/list.php?category_search=1&reset_category=false&brand_search=36%2C173%2C49%2C34%2C47%2C10%2C24%2C17%2C12%2C11%2C170%2C14%2C27%2C41%2C40%2C172%2C16%2C13%2C7%2C77%2C98%2C55%2C54%2C51%2C153%2C53%2C48%2C162%2C92%2C30%2C159%2C59%2C4%2C9999&state_search=Sold&orderby=lot_asc"

            yield scrapy.Request(url, callback=self.parse_page, headers=self.headers, meta={"cookies": cookie})

    def parse_page(self, response):

        total = response.xpath("//p[@class='kazu']/text()").extract()[0]
        total = re.findall(r"\d+", total)[0]
        print(total)
        if int(total) // 100:
            page_num = int(total) / 100 + 1
        else:
            page_num = int(total) / 100
        price = response.xpath("//span[@class='price']/text()").extract()
        for i in price:
            print("登录后获取的价格", i.strip())
        # for page in range(1):
        for page in range(page_num):
            page_op = str(page+1) + "_type" + str(self.type_num)
            url = "https://www.aucmarketplace.com/products/list.php?brand_search=36%2C173%2C49%2C34%2C47%2C10%2C24%2C17%2C12%2C11%2C170%2C14%2C27%2C41%2C40%2C172%2C16%2C13%2C7%2C98%2C55%2C54%2C51%2C153%2C48%2C162%2C92%2C30%2C159%2C59%2C4%2C9999&category_search=1&disp_number=100&orderby=lot_asc&MAKER_CD=36%2C173%2C49%2C34%2C47%2C10%2C24%2C17%2C12%2C11%2C170%2C14%2C27%2C41%2C40%2C172%2C16%2C13%2C7%2C98%2C55%2C54%2C51%2C153%2C48%2C162%2C92%2C30%2C159%2C59%2C4%2C9999&genre_cd=1&pageno=" + str(page + 1)
            cookie = response.meta["cookies"]

            # yield scrapy.Request(url, callback=self.parse, errback=self.errorback, headers=self.headers,
            #                      meta={"cookies": cookie, "op": page_op, "page": page, 'dont_redirect': True})

    def parse(self, response):
        item = AucnetItem()
        page_op = response.meta['op']
        page = response.meta['page']
        product_list = response.xpath("//ul[@id='tab_cont']/li/div/div")
        cookie = response.meta['cookies']
        item['currency'] = 'JPY'

        for product in product_list:
            product_op = page_op + "_" + str(page+1) + "_" + str(len(product_list))
            try:
                detail_url = product.xpath(".//p[@class='item_no']/a/@href").extract()[0]
                item["detail_url"] = "https://www.aucmarketplace.com" + detail_url
                print(item['detail_url'])
            except Exception as e:
                print(e)

            try:
                item['title'] = product.xpath(".//p[@class='ttl_new']/text()").extract()[0]
                # print(item['title'])
            except Exception as e:
                print(e)

            try:
                item['product_id'] = product.xpath(".//p[@class='item_no']/a/text()").extract()[0]
                # print(item['product_id'])
            except Exception as e:
                print(e)

            # 判断product_id是否在数据库中
            pro = MysqlTransaction()
            pro_data = pro.is_data(item['product_id'])
            if pro_data:
                item['title'] = pro_data[1]
                item['price'] = pro_data[2]
                item['original_price'] = pro_data[3]
                item['official_retail_price'] = pro_data[4]
                item['sku'] = pro_data[6]
                item['brand'] = pro_data[7]
                item['model'] = pro_data[8]
                item['material'] = pro_data[9]
                item['color'] = pro_data[10]
                item['size'] = pro_data[11]
                item['sex'] = pro_data[12]
                item['type'] = pro_data[13]
                item['subtype'] = pro_data[14]
                item['origin_condition'] = pro_data[15]
                item['photo_list'] = pro_data[16].split(",")
                item['sell_date'] = pro_data[17]
                item['sold_date'] = pro_data[18]
                item['crawl_date'] = self.times
                item['web_name'] = 'Aucnet'
                item['web_info'] = pro_data[20].replace("aucnet", "Aucnet")
                item['web_store_info'] = pro_data[21]
                item['vendor_info'] = pro_data[22]
                item['standard_condition'] = pro_data[23]
                item['full_content'] = pro_data[24]
                item['official_price'] = pro_data[25]
                item['condition_new_price'] = pro_data[26]
                # item['detail_url'] = full
                yield item
            #
            else:
                url = item['detail_url']

                yield scrapy.Request(url, callback=self.parse_html, headers=self.headers,
                                     meta={"cookies": cookie, "item": item, "op": product_op,
                                           "product_id": item['product_id'], "title": item['title'],
                                           "dont_redirect": True})

    def parse_html(self, response):
        
        item = response.meta['item']
        print("解析网页")
        item['product_id'] = response.meta['product_id']
        item['title'] = response.meta['title']
        item['web_name'] = "aucnet"
        item['crawl_date'] = self.times
        item['type'] = 'bag'
        item['web_info'] = {"name": item['web_name'], "country": "Japan", "city": "",
                            "address": "", "phone": "",
                            "language": "", "image_resolution": "640*480",
                            "location": {"longitude": "", "Latitude": ""},
                            "currency": "", "business_type": ""}

        # try:
        #     item['start_price'] = response.xpath("//td[@class='price_detail_isLogin']/span/@data-price").extract()[0]
        # except Exception as e:
        #     print(e)
        try:
            item['price'] = response.xpath("//span[@id='dyn_price_kekka_kng']/@data-price").extract()[0]
            print("价格", item['price'])
        except Exception as e:
            print(e)
        try:
            item['brand'] = response.xpath("//span[@class='brand_name']/text()").extract()[0]
        except Exception as e:
            print(e)
        try:
            item['title'] = item['brand'] + response.xpath("//span[@class='brand_type']/text()").extract()[0]
        except Exception as e:
            print(e)
        try:
            photo_list = []
            pre_photo_list = response.xpath("//div[@id='gallery_01']/a/img/@src").extract()
            newpre_photo_list = list(set(pre_photo_list))
            newpre_photo_list.sort(key=pre_photo_list.index)
            if newpre_photo_list:
                for photo in newpre_photo_list:
                    newphoto = photo + "#id=" + item['sku'] + "&v_" + str(pre_photo_list.index(photo) + 1)
                    photo_list.append(newphoto)
            item[photo_list] = photo_list
        except Exception as e:
            print(e)

        if item['currency'] != "" or item['currency']:
            if item['currency'] in self.exchange_rate_dict.keys():
                exchange_rate = self.exchange_rate_dict[item['currency']]
            else:
                exchange_rate = self.conversion_price(item['currency'])
                self.exchange_rate_dict[item['currency']] = exchange_rate
        else:
            exchange_rate = 1.0
        try:
            item['exchange_rate'] = exchange_rate
        except Exception as e:
            print(e)
        try:
            item['type'] = 'handbag'
        except Exception as e:
            print(e)
        try:
            item['origin_condition'] = response.xpath("//tbody/tr[3]/td/div[@class='line-break']/text()").extract()[0]
            print(item['origin_condition'])
        except Exception as e:
            print(e)
        try:
            standard_condition = response.xpath("//div[@class='item_detail_main02']/div/table/tbody/tr/td[1]/text()").extract()[0]
            standard_condition = standard_condition.strip()[-1]
            print(standard_condition)
            if standard_condition == 'S':
                item['standard_condition'] = 10
            elif standard_condition == 'A':
                item['standard_condition'] = 9
            elif standard_condition == 'B':
                item['standard_condition'] = 8.5
            elif standard_condition == 'C':
                item['standard_condition'] = 8
            else:
                item['standard_condition'] = 7
        except Exception as e:
            print(e)

        yield item

    def all_dict_setting(self, page_num, product_num):
        self.all_dict[page_num] = {}
        type_num = re.findall(r'type(\d+)', page_num)[0]
        page = re.findall(r'(\d+)_', page_num)[0]
        self.all_dict[page_num]['page_num'] = page
        self.all_dict[page_num]['product_num'] = product_num
        self.all_dict[page_num]['response_num'] = product_num
        self.all_dict[page_num]['left_num'] = 0
        self.all_dict[page_num]['left_url'] = {}
        self.all_dict[page_num]['status'] = 200
        self.all_dict[page_num]['type_num'] = type_num

    def conversion_price(self, currency):
        proxies = GetProxy()
        proxy = proxies.get_proxy()
        url = "https://freecurrencyrates.com/api/action.php?s=fcr&iso=" + currency + "&f=USD&v=1&do=cvals&ln=zh-hans"
        headers = {
            "Proxy-Authorization": proxy[0],
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        }
        s = requests.Session()
        res = s.get(url, headers=headers, proxies=proxy[-1], timeout=3)
        res.encoding = "utf-8"
        result = json.loads(res.text)

        exchange_rate = float(result[currency])

        return exchange_rate

    def closed(self, spider):
        with open(self.name + "_page_detail.json", "w") as f:
            for i in sorted(self.all_dict):
                jsons = json.dumps(self.all_dict[i])
                f.write(jsons+"\n")

                if self.all_dict[i]['status'] != 200:
                    with open(self.name+"_error_detail.json", "w") as p:
                        p.write(jsons+"\n")

    def errorback(self, failure):
        if failure.check(HttpError):
            # 保存错误信息
            count = ""
            response = failure.value.response
            page_op = response.meta['op']
            page_num = re.findall(r'.+(\d+)', page_op)
            if page_num:
                page_num = page_num[0]
                count = re.findall(r'.+(\d+)', page_op)[0]
                current_response_num = int(self.all_dict[page_num]['response_num']) - 1
                self.all_dict[page_num]['status'] = response.status
                self.all_dict[page_num]['response_num'] = current_response_num
                self.all_dict[page_num]['left_num'] += 1
                self.all_dict[page_num]['left_url'][response.url] = 1
                self.all_dict[page_num]['count'] = count  # 当前第几个错误
            else:
                self.all_dict[page_op] = {}
                self.all_dict[page_op]['left_url'] = {}
                self.all_dict[page_op]['status'] = response.status
                self.all_dict[page_op]['left'][response.url] = 1


class MysqlTransaction(object):
    def __init__(self):
        self.db = pymysql.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="123456",
            database="myspiderdb",
            charset="utf8"
        )

        # 游标对象
        self.cursor = self.db.cursor()

    def select_data(self):
        item = [
            'product_id', 'title', 'price', 'original_price', 'official_retail_price', 'currency', 'sku',
            'brand', 'model', 'material', 'color', 'size', 'sex', 'type', 'subtype', 'origin_condition', 'photo_list',
            'sell_date', 'sold_date', 'crawl_date', 'web_info', 'web_store_info',
            'vendor_info', 'standard_condition', 'full_content', 'official_price', 'condition_new_price'
        ]
        oneday = time.strftime('%Y-%m-%d', time.localtime(time.time()-86400*1))
        twoday = time.strftime('%Y-%m-%d', time.localtime(time.time()-86400*2))

        brand_name = 'aucnet'
        sql_select = "select " + ','.join(item) + " from AllData where web_name='" + brand_name.lower() +"' and (crawl_date='" + str(oneday) +"' or crawl_date='" + str(twoday)+"')"

        self.cursor.execute(sql_select)

        result = self.cursor.fetchall()

        self.db.commit()

        result_dict = {}

        for i in result:
            result_dict[i[0]] = i

        return result_dict

    # 判断数据库中是否在该product_id
    def is_data(self, product_id):
        all_data = self.select_data()
        if product_id in all_data.keys():
            print("在数据库中")
            # 用数据库中的信息补全
            pro_data = all_data[product_id]
        else:
            pro_data = ""

        return pro_data

    def close(self):
        self.cursor.close()
        self.db.close()

        print("数据库断开")


class GetProxy(object):
    def __init__(self):
        self._version = sys.version_info
        self.is_python3 = (self._version[0] == 3)
        self.orderno = "ZF20196174661xISNxM"
        self.secret = "864a96fcceb44a98a3824b6cbf389050"
        self.ip = "forward.xdaili.cn"
        self.port = "80"

    def encryption(self):
        timestamp = str(int(time.time()))
        string = ""
        string = "orderno=" + self.orderno + "," + "secret=" + self.secret + "," + "timestamp=" + timestamp

        if self.is_python3:
            string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()
        sign = md5_string.upper()
        auth = "sign=" + sign + "&" + "orderno=" + self.orderno + "&" + "timestamp=" + timestamp
        # header = auth

        return auth

    def get_proxy(self):
        ip_port = self.ip + ":" + self.port
        proxy = {"http": "http://" + ip_port, "htpps": "https://" + ip_port}

        return [self.encryption(), proxy]
