#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import json
import logging.handlers
import re
import sys
import time
import timeit
import types
from random import randint
from urllib.parse import parse_qs, urlparse, urlencode

import requests
import xlwt
from pypinyin import lazy_pinyin

ezxf = xlwt.easyxf

from bs4 import BeautifulSoup, Tag

### log 相关设置
# 设置时间格式
DATE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

logFormatter = logging.Formatter('%(threadName)10s %(asctime)s %(levelname)s [line:%(lineno)d] %(message)s')
log = logging.getLogger(__name__)

fileHandler = logging.handlers.RotatingFileHandler("full_logs.log", maxBytes=(15 * 1024 * 1024), backupCount=7,
                                                   encoding='utf-8')
# fileHandler = logging.FileHandler("full_logs.log", encoding='utf-8')
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.DEBUG)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.ERROR)
log.addHandler(consoleHandler)


def eye_catching_logging(msg='', logger=log.info):
    dashes = '-' * 50
    msg = '%s %s %s' % (dashes, str(msg).title(), dashes)
    logger(msg)


log.eye_catching_logging = eye_catching_logging


def list_debug(l: list):
    line_number = inspect.stack()[1][2]
    log.eye_catching_logging('called from [line:%s]' % (line_number))

    posfix = 'OF PRINTING LIST with size of [{length}]'.format(length=len(l))

    log.eye_catching_logging('{position} {posfix}'.format(position='start', posfix=posfix))
    for v in l:
        log.debug(v)
    log.eye_catching_logging('{position} {posfix}'.format(position='end', posfix=posfix))


log.list_debug = list_debug


def json_debug(var):
    line_number = inspect.stack()[1][2]
    log.eye_catching_logging('called from [line:%s]' % (line_number))
    log.debug(json.dumps(var, ensure_ascii=False, indent=2))
    pass


log.json_debug = json_debug

### requests 设置
meituan_waimai_url = 'http://waimai.meituan.com'

headers = {
    # "Host": "waimai.meituan.com",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "DNT": "1",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Referer": "http://waimai.meituan.com",
    "Accept-Language": "en,zh-CN;q=0.8,zh;q=0.6,zh-TW;q=0.4,en-GB;q=0.2,ja;q=0.2",
    "Cookie":
        "BAIDUID=5365A55222D580D81C224BB2827B9BBD:FG=1; "
        "PSTM=1488433005; BIDUPSID=31FB76D71AEF46DDEDAB7059DACCD5B6; "
        "BDUSS=mpZeEQybW9uTzlmRUowTEl0UnlXQ3FtMWdWSHFlV0s2OGVGdHE5QUpGM1NtLXRZSVFBQUFBJCQAAAAAAAAAAAEAAAAx-PUbt-fWrsHo6eQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANIOxFjSDsRYc; "
        "cflag=15%3A3; "
        "BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; "
        "w_uuid=kmIPS3P4B38ydNA-3Yl9Vn5TzEGkTuG59D2C4pKPtlt6Y37qEPCb7eO4xLiGV-3x; "
        "rvd=27303032; "
        "abt=1489757394.0%7CBDE; "
        "rvct=59; "
        "ci=20; "
        "__mta=142562829.1489572822289.1489757414882.1489757425452.4; "
        "uuid=aaed622404d6d7fea9a0.1489572821.0.0.0; "
        "oc=VGWS9bnksswT-gz8M7PP-Ne2q5g07ua8nfubsP9-rEXUnmQrxtF3jDBs3H6L0QNcaHHphDGejyd7HvPsGDgzOvM4voY-wYZmDkVOx-pagiHERjILjD3HpqtkPiYMhhKpblRJbv9DTGRCNtag10fg6NGJIbzp5xyspZpoaiF5aVc; "
        "__utma=211559370.1817606946.1489557637.1489572806.1489757397.2; "
        "__utmz=211559370.1489572806.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=zt_search; "
        "__utmv=211559370.|1=city=hangzhou=1^3=dealtype=11=1; "
        "_ga=GA1.2.1817606946.1489557637; "
        "w_cid=440111; "
        "w_cpy_cn=\"%E7%99%BD%E4%BA%91%E5%8C%BA\"; "
        "w_cpy=baiyunqu; "
        "waddrname=\"%E7%BE%8E%E4%BC%98%E4%B9%90%28%E9%92%9F%E8%90%BD%E6%BD%AD%E5%BA%97%29\"; "
        "w_geoid=ws0th9r1hpzn; "
        "w_ah=\"23.38598694652319,113.41067299246788,%E7%BE%8E%E4%BC%98%E4%B9%90%28%E9%92%9F%E8%90%BD%E6%BD%AD%E5%BA%97%29|23.38598694652319,113.41067299246788,%E6%9C%AA%E7%9F%A5|20.559364277869463,109.84969820827246,%E6%B9%9B%E6%B1%9F%E5%B8%82%24%E9%9B%B7%E5%B7%9E%E5%B8%82%24%24%E7%BE%8E%E4%BC%98%E4%B9%90%28%E9%BE%99%E9%97%A81%E5%BA%97%29|20.336991380900145,110.18095470964909,%E6%B9%9B%E6%B1%9F%E5%B8%82%24%E5%BE%90%E9%97%BB%E5%8E%BF%24%24%E7%BE%8E%E4%BC%98%E4%B9%90%28%E9%87%91%E8%B4%B8%E5%BA%97%29|30.084730871021748,120.06984293460846,%E6%9D%AD%E5%B7%9E%E7%BE%8E%E4%BC%98%E4%B9%90%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8|21.270870845764875,110.33403977751732,%E7%BE%8E%E4%BC%98%E4%B9%90%28%E9%BA%BB%E7%AB%A01%E5%BA%97%29|23.30090392380953,113.36225274950266,%E7%BE%8E%E4%BC%98%E4%B9%90%28%E5%A4%AA%E5%92%8C%E5%BA%97%29|23.176579847931862,113.26622597873211,%E5%B0%8A%E5%AE%9D%E6%AF%94%E8%90%A8%28%E6%9C%BA%E5%9C%BA%E8%B7%AF%E5%BA%97%29|23.18809188902378,113.27573172748089,%E5%A4%96%E5%A9%86%E5%AE%B6|23.178626876324415,113.26014876365662,%E6%96%B0%E5%AE%A2%E5%AE%B6%28%E8%BF%9C%E6%99%AF%E8%B7%AF%E5%BA%97%29\";"
        "JSESSIONID=196iown7kardy1amnqmutiy82x; _"
        "ga=GA1.3.1817606946.1489557637; _"
        "gat=1; __"
        "mta=142562829.1489572822289.1489757425452.1490092529677.5; "
        "w_utmz=\"utm_campaign=(direct)&utm_source=(direct)&utm_medium=(none)&utm_content=(none)&utm_term=(none)\"; "
        "w_visitid=c5ba70c7-4160-42b9-b168-0a9eabc359b8"

}

session = requests.session()
session.headers = headers

## xls heading相关设置
shop_heading = [
    'origin_price',
    'price',
    'id',
    'name',
    'isSellOut',
    'month_sold_count',
    'description',
    'zan',
    'minCount',
]

SHOP_NAME = 'shop_name'
shops_heading = [SHOP_NAME]
shops_heading += shop_heading

shops_info_heading = [
    'name',
    'address',
    'lat',
    'lng',
    'month_sale_count',
    'start_price',
    'send_price',
    'send_time',
    'url',
]

heading_tpye = {
    SHOP_NAME: 'text',
    'origin_price': 'float',
    'price': 'float',
    'id': 'int',
    'name': 'text',
    'isSellOut': 'bool',
    'month_sold_count': 'int',
    'description': 'text',
    'zan': 'int',
    'minCount': 'int',

    'address': 'text',
    'lat': 'float',
    'lng': 'float',
    'month_sale_count': 'text',
    'start_price': 'text',
    'send_price': 'text',
    'send_time': 'text',
    'url': 'text',
}

heading_cn = {
    SHOP_NAME: '商铺名',
    'origin_price': '原价',
    'price': '现价',
    'id': 'id',
    'name': '名称',
    'isSellOut': '售罄',
    'month_sold_count': '月销量',
    'description': '描述',
    'zan': '点赞数',
    'minCount': '单次最小购买量',

    'address': '地址',
    'lat': '纬度',
    'lng': '经度',
    'month_sale_count': '月销量',
    'start_price': '起送价',
    'send_price': '配送费',
    'send_time': '平均送餐时间',
    'url': '{current_time}:当前店铺网址（PS:美团外卖为防爬虫，每隔一段时间店铺的id会更新，对应的网址也会变化)'.format(current_time=time.ctime()),
}


def change_type(val, type_):
    if type_ == 'bool':
        return bool(val)
    elif type_ == 'float' and val is not None:
        return float(val)
    elif type_ == 'int' and val is not None:
        return int(val)
    elif not val:
        return ''
    else:
        return str(val)


type_fmt = {
    'text': ezxf(),
    'float': ezxf(num_format_str='#,##0.00'),
    'int': ezxf(num_format_str='#,##0'),
    'bool': ezxf(num_format_str='#,##0'),
}


######################################################################
class CityIdName(object):
    def __init__(self, city_id: str, city_name: str):
        self.id = city_id
        self.name = city_name

    def __str__(self):
        return 'id: %s, name: %s' % (self.id, self.name)


class Shop(object):
    def __init__(self, name: str, address: str, lat: str, lng: str, geo_hash='', urls=None):
        self.name = name
        self.address = address
        self.lat = lat
        self.lng = lng
        self.geo_hash = geo_hash
        if urls:
            self.urls = urls
        else:
            self.urls = []

        self.month_sale_count = None

    def __str__(self):
        # TODO: google it for if it can strify automatically
        return 'name: %s, address: %s, lat: %s, lng: %s, geo_hash: %s, url: %s' % (
            self.name, self.address, self.lat, self.lng, self.geo_hash, self.urls)


class MeituanCrawler(object):
    def __init__(self):
        self.shop_index = 0
        self.wb = xlwt.Workbook(encoding='utf-8')

    def export_shop_to_xls_sheet(self, parsed_info, sheet_name):
        if len(parsed_info) == 0:
            return

        ws = self.wb.add_sheet(sheet_name)  # type: xlwt.Worksheet

        # 写入heading
        row = 0
        for col, h in enumerate(shop_heading):
            ws.write(row, col, heading_cn[h])

        # 写入记录
        for food in parsed_info:
            row += 1
            for col, h in enumerate(shop_heading):
                ws.write(row, col, change_type(food[h], heading_tpye[h]), type_fmt[heading_tpye[h]])
        pass

    def export_one_shop(self, parsed_info, unique_file_name):
        log.eye_catching_logging('开始准备导出{filename}'.format(filename=unique_file_name))

        self.export_shop_to_xls_sheet(parsed_info, unique_file_name)

        log.eye_catching_logging('完成导出{filename}'.format(filename=unique_file_name))
        log.debug('')
        pass

    def get_sheet_name(self, filename):
        return re.sub(r'\[|\]|:|\\|\?|/*|\x00', '', filename)[:31]

    def parse_shop_page(self, shop: Shop):
        return self.parse_urls([shop.url], shop.name, shop.address)

    def parse_urls(self, urls, name='商铺', address=''):
        parsed_infos = []

        for idx, shop_url in enumerate(urls):
            res = session.get(shop_url)

            soup = BeautifulSoup(res.text, 'lxml')

            # 获取基本信息
            food_data_nodes = soup.find_all('script', {'type': 'text/template', 'id': re.compile('foodcontext-\d+')})

            parsed_info = []
            for food_data_node in food_data_nodes:  # type: Tag
                # TODO: add class product
                try:
                    food = json.loads(food_data_node.string)
                except json.decoder.JSONDecodeError as e:
                    log.error(e)
                    log.error(food_data_node)

                log.eye_catching_logging('提取 [{name}] 的信息'.format(name=food.get('name')))

                container = food_data_node.parent  # type: Tag

                # ------------------------如果存在食物描述，则获取-------------------
                food_description = container.find('div', {
                    'class': 'description'
                })
                if food_description and food_description.string:
                    food_description = food_description.string.strip()
                else:
                    food_description = None

                log.debug('描述 : %s' % food_description)

                # ------------------------如果存在点赞数，则获取-------------------
                food_zan = container.find('div', {
                    'class': 'zan-count'
                })
                if food_zan and food_zan.span and food_zan.span.string:
                    food_zan = food_zan.span.string.strip()[1:-1]
                else:
                    food_zan = None

                log.debug('点赞数 : %s' % food_zan)

                # ------------------------如果存在当月销量，则获取-------------------
                food_sold_count = container.find('div', {
                    'class': 'sold-count'
                })
                if food_sold_count and food_sold_count.span and food_sold_count.span.string:
                    # 原始的数据类似于： 月售12份
                    food_sold_count = food_sold_count.span.string.strip()

                    # 从中提取销售量
                    cnt_pattern = '月售(\d+)份'
                    food_sold_count = re.search(cnt_pattern, food_sold_count).group(1)
                else:
                    food_sold_count = None
                log.debug("count : %s", food_sold_count)

                parsed_info.append({
                    'id': food.get('id'),
                    'name': food.get('name'),
                    'price': food.get('price'),
                    'origin_price': food.get('origin_price'),
                    'minCount': food.get('minCount'),
                    'isSellOut': food['sku'][0]['isSellOut'],
                    'description': food_description,
                    'zan': food_zan,
                    'month_sold_count': food_sold_count
                })
                pass

            if parsed_info:
                parsed_infos.append(parsed_info)

            # 从详情页中获取商铺名
            details_list = soup.select('div.details .list .na')[0]  # type: Tag
            shop_name = details_list.find_all('span')[0].string.strip()

            # TODO: 从详情页中获取商铺地址
            # shop_address_div = soup.select('div.rest-info-thirdpart')[0]
            # shop_address = shop_address_div.string.strip().replace('商家地址：', '')

            self.shop_index += 1
            shop_unique_name = '{idx}_{shop_name}@{shop_address}'.format(idx=self.shop_index,
                                                                         shop_name=shop_name,
                                                                         shop_address=address.replace('$', ''))
            if idx > 0:
                shop_unique_name += '_{index}'.format(index=idx)
            shop_unique_name += '_商品信息'

            unique_file_name = self.get_sheet_name(shop_unique_name)

            # 将当前商家导出
            self.export_one_shop(parsed_info, unique_file_name)

        return parsed_infos

    def is_shop_in_this_city(self, address: str, shop_name: str, city_name: str):
        return shop_name in address and city_name in address

    def export_all_to_xls_sheet(self, parsed_infos, sheet_name):
        if len(parsed_infos) == 0:
            return

        ws = self.wb.add_sheet(sheet_name)
        # 写入heading
        row = 0
        for col, h in enumerate(shops_heading):
            ws.write(row, col, heading_cn[h])

        # 写入记录
        for shop_name, parsed_info in parsed_infos.items():
            for food in parsed_info:
                row += 1
                # 添加商店名信息
                food[SHOP_NAME] = shop_name
                # 将数据一行行写入表单
                for col, h in enumerate(shops_heading):
                    ws.write(row, col, change_type(food[h], heading_tpye[h]), type_fmt[heading_tpye[h]])
            pass

        log.eye_catching_logging('成功导出为{sheetname}表单'.format(sheetname=sheet_name))
        pass

    def export_all_shops(self, parsed_infos: dict, filename):
        log.eye_catching_logging('开始准备导出{filename}'.format(filename=filename))

        self.export_all_to_xls_sheet(parsed_infos, filename)

        log.eye_catching_logging('完成导出{filename}'.format(filename=filename))
        log.info('')
        pass

    def is_the_shop_we_want(self, res_name, shop_name):
        return shop_name in res_name

    def parse_shops_and_export(self, shops: list, shop_name: str):
        if len(shops) == 0:
            log.eye_catching_logging('商家列表为空')
            return
        log.eye_catching_logging('开始解析商家页面')

        parsed_infos = {}
        for shop in shops:
            for idx, parsed_info in enumerate(self.parse_shop_page(shop)):
                shop_unique_name = '{name}@{address}'.format(name=shop.name, address=shop.address.replace('$', ''))
                if idx > 0:
                    shop_unique_name += '_{index}'.format(index=idx)

                parsed_infos[shop_unique_name] = parsed_info

        # log.json_debug(parsed_infos)

        # 将本次获取的商家信息导出到单个汇总的表单
        filepath = '{shop_name}_商品信息_汇总'.format(shop_name=shop_name)
        self.export_all_shops(parsed_infos, self.get_sheet_name(filepath))

        return parsed_infos

    def export_shops_info_to_xls_sheet(self, shops, sheetname):
        ws = self.wb.add_sheet(sheetname)  # type: xlwt.Worksheet

        row = 0
        for col, h in enumerate(shops_info_heading):
            ws.write(row, col, heading_cn[h])
        ws.write(row, len(shops_info_heading), 'geo_hash')

        for shop in shops:
            row += 1
            for col, h in enumerate(shops_info_heading):
                # NOTE: 这里需要str，由其针对urls:list，否则会产生错误
                ws.write(row, col, change_type(shop.__getattribute__(h), heading_tpye[h]), type_fmt[heading_tpye[h]])
            ws.write(row, len(shops_info_heading), str(shop.geo_hash))

        log.eye_catching_logging('成功导出为{sheetname}表单'.format(sheetname=sheetname))
        pass

    def remove_duplicate_shops(self, shops):
        unique_shops = []
        visited_urls = {}

        for shop in shops:
            if not visited_urls.get(shop.url):
                unique_shops.append(shop)
                visited_urls[shop.url] = True

        return unique_shops

    def filter_out_shop_with_no_urls(self, shops):
        filtered = list(filter(lambda shop: shop.urls, shops))

        log.eye_catching_logging('美团上该品牌开设{number_of_shop}家的店面如下所示'.format(number_of_shop=len(filtered)))
        log.list_debug(filtered)

        return filtered

    def get_striped_str(self, res_tag_with_str):
        if res_tag_with_str and res_tag_with_str.string:
            res_tag_with_str = res_tag_with_str.string.replace('\n', '').strip()
        else:
            res_tag_with_str = ''

        return res_tag_with_str

    def get_shop_with_url_by_geo_hash_and_name(self, shop: Shop):
        query = {'keyword': shop.name}
        meituan_search_api = 'http://waimai.meituan.com/search/{geo_hash}/rt?{query}'.format(
            geo_hash=shop.geo_hash, query=urlencode(query))

        res = session.get(meituan_search_api)

        log.eye_catching_logging('start find shop url in search results')

        soup = BeautifulSoup(res.text, 'lxml')

        res_lis = soup.find_all('li', {'class': 'rest-list'})
        # log.debug(res_lis)

        if len(res_lis) == 0:
            log.eye_catching_logging()
            log.warning(
                'fail to find [{shop}] url in : {search_url}'.format(search_url=meituan_search_api, shop=shop.address))
            log.eye_catching_logging()

        shops_in_res = []

        for res_li in res_lis:
            res_name = res_li.find('p', {'class': 'name'}).string.replace('\n', '').strip()
            res_path = res_li.find('a')['href']

            res_total = self.get_striped_str(res_li.find('span', {'class': 'total'})).replace('月售', '')
            res_start_price = self.get_striped_str(res_li.find('span', {'class': 'start-price'})).replace('起送', '')

            res_send_price = self.get_striped_str(res_li.find('span', {'class': 'send-price'})).replace('配送费', '')
            res_send_time = self.get_striped_str(res_li.find('p', {'class': 'send-time'})).replace('平均送餐时间：', '')

            log.debug([res_total, res_start_price, res_send_price, res_send_time])

            # 检查该搜索结果是否为我们想要的结果 ： 看品牌名是否在搜索结果的标题中
            if self.is_the_shop_we_want(res_name, shop.name):
                log.debug('SUCCESSED in finding url in : {search_url}'.format(search_url=meituan_search_api))
                log.debug("result shop name is : %s" % res_name)
                log.debug("result shop path is : %s" % res_path)

                if res_path:
                    shop_url = '{host}{path}'.format(host=meituan_waimai_url, path=res_path)

                    shop_in_res = Shop(res_name, shop.address, shop.lat, shop.lng, shop.geo_hash)
                    # TODO: add elems
                    shop_in_res.url = shop_url
                    shop_in_res.month_sale_count = res_total
                    shop_in_res.start_price = res_start_price
                    shop_in_res.send_price = res_send_price
                    shop_in_res.send_time = res_send_time

                    log.debug('url is : {url}'.format(url=shop_url))

                    shops_in_res.append(shop_in_res)

        # log.debug(shop)
        return shops_in_res
        pass

    def batch_get_shop_with_url_by_geo_hash_and_name(self, shops):
        shops_exists_in_meituan = []
        for shop in shops:
            if shop.geo_hash:
                shops_exists_in_meituan += self.get_shop_with_url_by_geo_hash_and_name(shop)

        return shops_exists_in_meituan

    def fetch_geo_hash_for_shops(self, shops: list):
        log.eye_catching_logging('start fetch geo hash')
        meituan_calc_geo_hash_api = 'http://waimai.meituan.com/geo/geohash'

        for idx, shop in enumerate(shops):
            query = {
                'lat': shop.lat,
                'lng': shop.lng,
                'addr': shop.address,
                'from': 'm',
            }

            MAX_TRIES = 5
            while MAX_TRIES:
                res = session.get(meituan_calc_geo_hash_api, params=query)
                shop.geo_hash = res.cookies.get('w_geoid')

                if shop.geo_hash:
                    break

                # if goes here, access limit is exceed
                up = urlparse(res.url)
                returned_params = parse_qs(up.query)

                log.debug(res.url)
                log.debug('returned_params is : %s' % returned_params)
                wait_for = randint(3, 4)

                log.warning(
                    'access limit is exceed when fetching [%dth] shop named [%s], wait for %ds, remaing try time: %d' % (
                        idx, shop.address, wait_for, MAX_TRIES))
                time.sleep(wait_for)
                MAX_TRIES -= 1

        log.eye_catching_logging('Geo hash fetched')
        log.list_debug(shops)

    def add_lng_lat_by_address(self, addresses: list, shop_name=''):
        bdmap_address_to_lng_lat_api = 'http://api.map.baidu.com/geocoder/v2/'
        application_key = 'Eze6dPlb3bnUrihPNaaKljdUosb4G41B'

        shops = []
        for address in addresses:
            query = {
                'output': 'json',
                'address': address,
                'ak': application_key
            }

            res = session.get(bdmap_address_to_lng_lat_api, params=query).json()
            log.debug(res)

            location = res['result']['location']
            shop = Shop(shop_name, address, location['lat'], location['lng'])
            shops.append(shop)

        log.list_debug(shops)
        return shops

    def find_possiable_addresses(self, cid_name: CityIdName, shop_name: str):
        def find_res_upper_limit(wd, cid, rn_l=0, rn_h=130):
            from functools import lru_cache
            @lru_cache()
            def _try(wd, cid, rn, max_try=5):
                res = session.get('http://map.baidu.com/su', params={
                    "wd": wd,
                    "cid": cid,
                    "rn": rn,
                    "type": "0",
                })
                res.encoding = 'utf-8'
                try:
                    return len(res.json().get('s')) != 0
                except Exception as e:
                    log.eye_catching_logging(str(e), log.error)
                    log.eye_catching_logging("sleep for 0.5s", log.error)
                    time.sleep(0.5)

                    if max_try <= 0:
                        log.eye_catching_logging('address get failed with max_try times', log.error)
                        return False
                    return _try(wd, cid, rn, max_try - 1)

            @lru_cache()
            def _rel(wd, cid, rn):
                # TTT for -1, TTF for 0, TFF,FFF for 1
                if _try(wd, cid, rn):
                    if _try(wd, cid, rn + 1):
                        return -1
                    else:
                        return 0
                else:
                    return 1

            rn_l = 0
            rn_h = 130
            if _try(wd, cid, rn_h):
                print('found at high', rn_h)
                return rn_h

            while True:
                rn = int((rn_l + rn_h) / 2)
                r = _rel(wd, cid, rn)
                if r == 0:
                    return rn
                elif r == -1:
                    rn_l = rn + 1
                else:
                    rn_h = rn - 1

                if rn_l > rn_h:
                    return -1

        bdmap_find_address_by_name_api = 'http://map.baidu.com/su'
        # note: 这个数可能会引起问题，之前65在广东华莱士会出现问题，其他地方不会
        # 采用二分法找到合适的结果数
        result_number = find_res_upper_limit(shop_name, cid_name.id, 0, 130)
        log.eye_catching_logging('合适的结果数为:%d' % result_number, log.error)

        query = {
            "wd": shop_name,
            "cid": cid_name.id,
            "rn": result_number,
            "type": "0",
        }

        while True:
            res = session.get(bdmap_find_address_by_name_api, params=query)

            # print(test.status_code)
            res.encoding = 'utf-8'
            try:
                json_res = res.json()
                break
            except Exception as e:
                log.eye_catching_logging(str(e), log.error)
                log.eye_catching_logging("sleep for 0.5s", log.error)
                time.sleep(0.5)

        addresses = []
        for address in json_res['s']:
            if not self.is_shop_in_this_city(address, shop_name, cid_name.name):
                continue
            addresses.append(address)

        log.eye_catching_logging('api response for %s' % cid_name)
        log.debug(json.dumps(json_res, ensure_ascii=False, indent=2))

        log.eye_catching_logging('%s' % cid_name)
        log.list_debug(addresses)
        log.eye_catching_logging('total %s' % (len(addresses)))

        return addresses

    def get_city_id_and_name(self, city_name: str):
        """
        :param city_name: 城市名称
        :return: [id:int, name:str]
        """
        ID = 0
        NAME = 1

        with open('BaiduMap_cityCode_1102.txt', encoding='utf-8') as city_ids:
            import csv

            for city_id_name in csv.reader(city_ids):
                if city_name in city_id_name[NAME]:
                    log.eye_catching_logging('city id found')
                    log.eye_catching_logging(city_id_name, log.error)

                    return CityIdName(*city_id_name)

            log.eye_catching_logging('%s not found in city list' % city_name, log.error)
            return [0, 'not found']

    def collect_shop_urls(self, city_name, shop_name):
        ## 处理逻辑
        # 1. 获取该城市对应的id，组成tuple
        cid_name = self.get_city_id_and_name(city_name)
        # 2. 利用百度地图接口找到该城市存在的该品牌的店的地址作为初始结果集
        addresses = self.find_possiable_addresses(cid_name, shop_name)

        shops_exists_in_meituan_unique = self.fetch_shop_url_by_address(addresses, city_name, shop_name)

        return shops_exists_in_meituan_unique

    def fetch_shop_url_by_address(self, addresses, city_name, shop_name):
        # 3. 利用百度的坐标反查接口获取这些地址对应的坐标值
        shops = self.add_lng_lat_by_address(addresses, shop_name)
        # 4. 利用坐标值和地址，通过美团外卖的接口获取该店（所在区域）在美团外卖内部系统内的地理哈希值
        self.fetch_geo_hash_for_shops(shops)
        # 5. 利用该地理哈希值和商店名称，通过美团的搜索接口尝试获取其店铺网址，获取其中所有的在美团上开设的该店铺信息
        shops_exists_in_meituan = self.batch_get_shop_with_url_by_geo_hash_and_name(shops)
        # 6. 对获取的店铺进行去重（根据URL）
        shops_exists_in_meituan_unique = self.remove_duplicate_shops(shops_exists_in_meituan)
        # 7. 将所有商店必要的统计信息导入到一个表单内
        shops_info_sheet_name = '{city_name}_{shop_name}'.format(city_name=city_name, shop_name=shop_name)
        self.export_shops_info_to_xls_sheet(shops_exists_in_meituan_unique, self.get_sheet_name(shops_info_sheet_name))
        return shops_exists_in_meituan_unique

    def run_crawler_and_export_with_shop_urls(self, urls, city_name, shop_name):
        # 根据url获取店铺地址
        addresses = self.get_addresses_by_urls(urls)
        # 根据地址获取店铺相关信息及url
        shops_exists_in_meituan = self.fetch_shop_url_by_address(addresses, city_name, shop_name)

        parse_shops_info = self.parse_shops_and_export(shops_exists_in_meituan, '')

    def run_crawler_and_export(self, city_name, shop_name):
        # 获取在该城市范围内该商店在美团上所开设的所有店铺的网址等信息
        shops_exists_in_meituan = self.collect_shop_urls(city_name, shop_name)

        # 对这些找到的店铺抓取其页面数据
        parse_shops_info = self.parse_shops_and_export(shops_exists_in_meituan, shop_name)

    def run(self, city_name='湛江', shop_name='美优乐', ids=''):
        """
        根据输入的城市名和商店名，找到该城市内该商店在美团所开设的所有店铺的商品的信息列表，并导出为xls文件
        :return:
        """
        # 1. 获取url
        # 2. 爬取内容
        # 3. 开发前端: 试试用Python写GUI
        ## 从用户获取城市和商店名
        # city_name = '湛江'
        # shop_name = '美优乐'

        log.eye_catching_logging('开始抓取[{city}]:[{shop}]'.format(city=city_name, shop=shop_name), log.error)
        if ids:
            shop_url = 'http://waimai.meituan.com/restaurant/{id}'
            ids = ids.split(',')
            urls = list(map(lambda x: shop_url.format(id=x.strip()), ids))

            self.run_crawler_and_export_with_shop_urls(urls, city_name.strip(), shop_name.strip())
        else:
            self.run_crawler_and_export(city_name.strip(), shop_name.strip())

        log.eye_catching_logging('完成抓取[{city}]:[{shop}]'.format(city=city_name, shop=shop_name), log.error)

        # TODO: 设置不同类型的格式，以及每个列对应的类型

        # global data_dir
        # # 确保数据文件夹已创建
        # data_dir = './结果/{shopname}'.format(shopname=shop_name, time=time.strftime(DATE_TIME_FORMAT))
        #
        # if not os.path.exists(data_dir):
        #     os.makedirs(data_dir)

        saved_file = '{current_time}_{location}_{shop}.xls'.format(
            current_time=time.strftime(DATE_TIME_FORMAT),
            location=city_name,
            shop=shop_name
        )

        res = [self.wb, saved_file]

        # log.info(res)

        return res

    def get_addresses_by_urls(self, urls: list):
        addresses = []
        # 从每个页面中抓取地址信息，并返回
        for shop_url in urls:
            res = session.get(shop_url)

            soup = BeautifulSoup(res.text, 'lxml')

            shop_address_div = soup.select('div.rest-info-thirdpart')[0]
            shop_address = shop_address_div.string.strip().replace('商家地址：', '')

            addresses.append(shop_address)

        return addresses

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def export_shop_to_xls_eleme(self, shops):
        wb = xlwt.Workbook(encoding='utf-8')

        if len(shops) == 0:
            wb.add_sheet('没有找到相关结果')
            return wb

        def patch_with_helper(worksheet):
            # 添加辅助方法
            def write_float(self, row, col, val):
                if val is None:
                    val = 0.0
                self.write(row, col, float(val), type_fmt['float'])

            def write_int(self, row, col, val):
                if val is None:
                    val = 0
                self.write(row, col, int(val), type_fmt['int'])

            def write_bool(self, row, col, val):
                if val is None:
                    val = False
                self.write(row, col, bool(val), type_fmt['bool'])

            worksheet.write_float = types.MethodType(write_float, worksheet)
            worksheet.write_int = types.MethodType(write_int, worksheet)
            worksheet.write_bool = types.MethodType(write_bool, worksheet)

            return worksheet

        # -------------------商家汇总信息--------------------------------
        ws = wb.add_sheet('商家汇总信息')  # type: xlwt.Worksheet
        ws = patch_with_helper(ws)

        # 写入heading
        ws.write(0, 0, '商铺名')
        ws.write(0, 1, '地址')
        ws.write(0, 2, '纬度')
        ws.write(0, 3, '经度')
        ws.write(0, 4, '月售单数')
        ws.write(0, 5, '起送价')
        ws.write(0, 6, '费送费')
        ws.write(0, 7, '平均送达时间')
        ws.write(0, 8, '评分')
        ws.write(0, 9, '评分数')
        ws.write(0, 10, '评分高于周边商家比例')
        ws.write(0, 11, '好评率')
        ws.write(0, 12, '菜品评分')
        ws.write(0, 13, '服务态度评分')
        ws.write(0, 14, '店铺网址')

        # 写入记录
        row = 0
        for shop in shops:  # type: dict
            row += 1

            ws.write(row, 0, shop.get('name'))
            ws.write(row, 1, shop.get('address'))
            ws.write_float(row, 2, shop.get('latitude'))
            ws.write_float(row, 3, shop.get('longitude'))
            ws.write_int(row, 4, shop.get('recent_order_num'))
            ws.write_int(row, 5, shop.get('float_minimum_order_amount'))
            ws.write_int(row, 6, shop.get('float_delivery_fee'))
            ws.write_int(row, 7, shop.get('order_lead_time'))
            ws.write_float(row, 8, shop.get('rating'))
            ws.write_int(row, 9, shop.get('rating_count'))
            ws.write_float(row, 10, shop.get('compare_rating'))
            ws.write_float(row, 11, shop.get('positive_rating'))
            ws.write_float(row, 12, shop.get('food_score'))
            ws.write_float(row, 13, shop.get('service_score'))
            ws.write(row, 14, shop.get('url'))

        # -------------------各家店商品信息--------------------------------
        for idx, shop in enumerate(shops):
            ws = wb.add_sheet(self.get_sheet_name('{index}_{name}@{address}'.format(index=idx, name=shop.get('name'),
                                                                                    address=shop.get(
                                                                                        'address'))))  # type: xlwt.Worksheet
            ws = patch_with_helper(ws)

            menu_for_shops_heading = [
                'original_price',
                'price',
                'item_id',
                'name',
                'sold_out',
                'month_sales',
                'packing_fee',
                'rating',
                'rating_count',
                'description'
            ]
            # 写入heading
            ws.write(0, 0, '原价')
            ws.write(0, 1, '现价')
            ws.write(0, 2, 'id')
            ws.write(0, 3, '名称')
            ws.write(0, 4, '售罄')
            ws.write(0, 5, '月销量')
            ws.write(0, 6, '打包费')
            ws.write(0, 7, '评分')
            ws.write(0, 8, '评分数')
            ws.write(0, 9, '描述')
            ws.write(0, 10, '规格')

            # 写入记录
            row = 0
            for sub_menu in shop.get('menu'):  # type: dict
                for food in sub_menu.get('foods'):  # type: dict
                    for specfood in food.get('specfoods'):  # type: dict
                        row += 1

                        ws.write_float(row, 0, specfood.get('original_price'))
                        ws.write_float(row, 1, specfood.get('price'))
                        ws.write_int(row, 2, specfood.get('food_id'))
                        ws.write(row, 3, specfood.get('name'))
                        ws.write_bool(row, 4, specfood.get('sold_out'))
                        ws.write_int(row, 5, specfood.get('recent_popularity'))
                        ws.write_float(row, 6, specfood.get('packing_fee'))
                        ws.write_float(row, 7, food.get('rating'))
                        ws.write_int(row, 8, food.get('rating_count'))
                        ws.write(row, 9, food.get('description'))
                        ws.write(row, 10, str(specfood.get('specs')))

        # -------------------各菜品信息（总计）--------------------------------
        # ---计算统计信息
        food_infos = self.compute_food_statistics(shops)  # -------导出统计信息
        ws = wb.add_sheet('菜品统计信息')  # type: xlwt.Worksheet
        ws = patch_with_helper(ws)

        # 写入heading
        ws.write(0, 0, '名称')
        ws.write(0, 1, '总销量')
        ws.write(0, 2, '总销售额')
        ws.write(0, 3, '平均销量')
        ws.write(0, 4, '平均销售额')
        ws.write(0, 5, '平均价格')
        ws.write(0, 6, '各门店总计展现次数（每个规格作为计数单位）')

        # 写入记录
        row = 0
        for food_info in food_infos:  # type: dict
            row += 1

            ws.write(row, 0, food_info.get('name'))
            ws.write_int(row, 1, food_info.get('total_sold_count'))
            ws.write_float(row, 2, food_info.get('total_sold_money'))
            ws.write_float(row, 3, food_info.get('average_sold_count'))
            ws.write_float(row, 4, food_info.get('average_sold_money'))
            ws.write_float(row, 5, food_info.get('average_price'))
            ws.write_int(row, 6, food_info.get('occur_times'))

        return wb
        pass

    def compute_food_statistics(self, shops):
        foods = []
        for shop in shops:  # type: dict
            for sub_menu in shop.get('menu'):  # type: dict
                for food in sub_menu.get('foods'):  # type: dict
                    for specfood in food.get('specfoods'):  # type: dict
                        foods.append({
                            'name': specfood.get('name'),
                            'price': float(specfood.get('price')),
                            'sold_count': int(specfood.get('recent_popularity')),
                            'food_id': int(specfood.get('food_id')),
                            'item_id': int(food.get('item_id'))
                        })

        import itertools
        from operator import itemgetter

        food_infos = []
        foods.sort(key=itemgetter("name"))
        for name, foods_with_same_name in itertools.groupby(foods, lambda food: food['name']):
            foods_with_same_name = list(foods_with_same_name)
            total_sold_count = sum([food['sold_count'] for food in foods_with_same_name])
            total_sold_money = sum([food['sold_count'] * food['price'] for food in foods_with_same_name])
            total_count = len(foods_with_same_name)

            food_infos.append({
                "name": name,
                "total_sold_count": total_sold_count,
                "total_sold_money": total_sold_money,
                "average_sold_count": total_sold_count / total_count,
                "average_sold_money": total_sold_money / total_count,
                "average_price": sum([food['price'] for food in foods_with_same_name]) / total_count,
                "occur_times": total_count,
            })

        # food_infos.sort(key=itemgetter(""))

        return food_infos

    def run_eleme(self, city_name, brand_name, ids: str):
        if not ids:
            # 使用城市和商家名进行搜素
            cid_name = self.get_city_id_and_name(city_name)
            ## TODO: 使用采集到的离线商铺信息进行匹配shops_exists_in_eleme_unique
            addresses = self.find_possiable_addresses(cid_name, brand_name)

            shops = self.add_lng_lat_by_address(addresses, brand_name)

            # 根据坐标获取商铺url
            shops_exists_in_eleme = self.batch_get_shop_with_url_by_lat_and_lng(shops, brand_name)

            # 移除重复结果
            shops_exists_in_eleme_unique = self.remove_duplicate_shops_eleme(shops_exists_in_eleme)
        else:
            # 使用商家名和ids进行搜索
            # 根据ids构造shops

            # 'brand': brand_name,
            # 'latitude': shop.lat,
            # 'longitude': shop.lng,
            # 'id': id,
            # 'url': 'https://www.ele.me/shop/{id}'.format(id=id)
            shop_url = 'https://www.ele.me/shop/{id}'

            shops_exists_in_eleme_unique = []
            for id in ids.split(','):
                shops_exists_in_eleme_unique.append({
                    'brand': brand_name,
                    'latitude': 0,
                    'longitude': 0,
                    'id': id.strip(),
                    'url': shop_url.format(id=id.strip())
                })

        # 解析每个页面，将相关信息添加到shop中
        self.parse_shops_eleme(shops_exists_in_eleme_unique, brand_name)

        # 导出结果

        filename = ''.join(lazy_pinyin('{current_time}_{location}_{shop}.xls'.format(
            current_time=time.strftime(DATE_TIME_FORMAT),
            location=city_name,
            shop=brand_name
        )))

        return [self.export_shop_to_xls_eleme(shops_exists_in_eleme_unique), filename]
        pass

    def batch_get_shop_with_url_by_lat_and_lng(self, shops, brand_name):
        # https://mainsite-restapi.ele.me/shopping/restaurants/search
        # extras[]:activity
        # keyword:外婆家 +++++++++++++
        # latitude:30.262373    +++++++++++++
        # limit:100
        # longitude:120.12105 +++++++++++++
        # offset:0
        # terminal:web

        # ?extras%5B%5D=activity&keyword=%E5%A4%96%E5%A9%86%E5%AE%B6&latitude=30.262373&limit=100&longitude=120.12105&offset=0&terminal=web

        # result => restaurant_with_foods->[0,1,2..n]->restaurant->id
        # url => https://www.ele.me/shop/{id}
        api = 'https://mainsite-restapi.ele.me/shopping/restaurants/search'
        query = {
            'extras[]': 'activity',
            'limit': 100,
            'offset': 0,
            'terminal': 'web',
        }

        shops_with_url = []
        for shop in shops:
            query['keyword'] = brand_name
            query['latitude'] = shop.lat
            query['longitude'] = shop.lng

            res = requests.get(api, params=query)
            res = res.json()
            ids = set()
            for restaurant in res['restaurant_with_foods']:
                ids.add(restaurant['restaurant']['id'])

            for id in ids:
                shops_with_url.append({
                    'brand': brand_name,
                    'latitude': shop.lat,
                    'longitude': shop.lng,
                    'id': id,
                    'url': 'https://www.ele.me/shop/{id}'.format(id=id)
                })

        return shops_with_url
        pass

    def remove_duplicate_shops_eleme(self, shops):
        unique_shops = []
        visited_urls = {}

        for shop in shops:
            if not visited_urls.get(shop['url']):
                unique_shops.append(shop)
                visited_urls[shop['url']] = True

        return unique_shops
        pass

    def parse_shops_eleme(self, shops_exists_in_eleme_unique, brand_name):
        _session = requests.session()

        from multiprocessing.dummy import Pool as ThreadPool
        pool = ThreadPool(8)

        # TODO: replace with pool
        for shop in shops_exists_in_eleme_unique:  # type: dict
            # 商家信息：https://mainsite-restapi.ele.me/shopping/restaurant/1387370?extras%5B%5D=activity&extras%5B%5D=license&extras%5B%5D=identification&extras%5B%5D=albums&extras%5B%5D=flavors&latitude=30.262373&longitude=120.12105
            # 坐标参数影响 [distance]
            # NOTE：根据该接口的结果中的latitude和longitude得到其坐标
            info_api = 'https://mainsite-restapi.ele.me/shopping/restaurant/{id}'.format(id=shop['id'])
            query = {
                'extras[]': [
                    'activity',
                    'license',
                    'identification',
                    'albums',
                    'flavors',
                ],
                'latitude': shop.get('latitude', 0),
                'longitude': shop.get('longitude', 0)
            }
            shop_info = _session.get(info_api, params=query).json()
            shop.update(shop_info)

            # 商家评价信息： https://mainsite-restapi.ele.me/ugc/v1/restaurants/1387370/rating_scores?latitude=30.262373&longitude=120.12105
            # 坐标影响结果中的  compare_rating 字段
            rating_api = 'https://mainsite-restapi.ele.me/ugc/v1/restaurants/{id}/rating_scores'.format(id=shop['id'])
            query = {
                # 若直接输入店铺ids，则无该信息
                'latitude': shop.get('latitude', 0),
                'longitude': shop.get('longitude', 0)
            }
            shop_ratings = _session.get(rating_api, params=query).json()
            shop.update(shop_ratings)

            # 菜品信息： https://mainsite-restapi.ele.me/shopping/v2/menu?restaurant_id=1387370
            menu_api = 'https://mainsite-restapi.ele.me/shopping/v2/menu'
            query = {
                'restaurant_id': shop['id']
            }
            while True:
                menu = _session.get(menu_api, params=query).json()
                if type(menu) is list:
                    # 正常情况下返回list
                    break
                else:
                    # 若返回结果为dict，则说明操作过频繁，休息一会儿
                    # {'name': 'SERVICE_REJECTED', 'message': '操作太频繁啦，请休息一下再试。'}
                    time.sleep(1)
                    pass
            shop['menu'] = menu


def timer(func, *args, **kwargs):
    ran_time = timeit.timeit(func, number=1)

    log.critical('method %s run %s seconds' % (func, ran_time))


ban_cnt = 0


def get_eleme_ids():
    global ban_cnt
    api = 'https://mainsite-restapi.ele.me/shopping/restaurant/{id}?latitude=30.262373&longitude=120.12105'

    # get start id
    # 目前观测到的最后一个六位数的id为  580703
    start_id = get_start_id_from_file()

    id = start_id
    valid_shops = []
    start_at = time.time()
    _session = requests.session()

    from multiprocessing.dummy import Pool as ThreadPool
    pool = ThreadPool(8)

    def _process_for_id(id):
        global ban_cnt
        prefix = '[%9d] : ' % id

        res = _session.get(api.format(id=id)).json()  # type: dict

        # 每次请求相隔0.1s恰好不会被ban, 0.5s屏蔽率为1%
        # time.sleep(0.05)

        if res.get('name') == 'RESTAURANT_NOT_FOUND':
            # log.error(prefix + res.get('message'))
            # time.sleep(0.05)
            pass
        elif res.get('name') == 'SYSTEM_ERROR':
            # log.error(prefix + res.get('message'))
            pass
        elif res.get('name') == 'OpenAPI 测试餐厅':
            pass
        elif res.get('name') == 'SERVICE_REJECTED':
            # log.error(prefix + res.get('message')+' :: 休息0.05s')
            # add mutex
            ban_cnt += 1
            # time.sleep(0.05)
            return _process_for_id(id)
        else:
            # http://api.map.baidu.com/geocoder/v2/?output=json&ak=Eze6dPlb3bnUrihPNaaKljdUosb4G41B&location=30.271933,120.1195
            # 根据坐标添加地理信息
            # {"status":0,"result":{"location":{"lng":120.11949999999993,"lat":30.271933048715849},"formatted_address":"浙江省杭州市西湖区西溪路","business":"西溪,西湖,古荡","addressComponent":{"country":"中国","country_code":0,"province":"浙江省","city":"杭州市","district":"西湖区","adcode":"330106","street":"西溪路","street_number":"","direction":"","distance":""},"pois":[],"poiRegions":[],"sematic_description":"秦亭山北123米","cityCode":179}}
            shop = {
                'id': id,
                'name': res.get('name'),
                'address': res.get('address'),
                'latitude': res.get('latitude'),
                'longitude': res.get('longitude'),
                # 'city_code': _session.get(baidu_api).json()['result']['cityCode'],
            }
            log.error(prefix + json.dumps(shop, ensure_ascii=False))
            return shop

    batch_size = 100
    batch_data_max_size = 5000
    while id <= 999999999:
        loop_start_at = time.time()
        last_res_cnt = len(valid_shops)

        results = list(filter(None, pool.map(_process_for_id, range(id, id + batch_size))))
        # results = filter(None, map(_process_for_id, range(id, id+batch_size)))
        valid_shops += results

        id += batch_size

        log_current_status(batch_size, id, last_res_cnt, loop_start_at, start_at, start_id, valid_shops)

        if last_res_cnt != len(valid_shops):
            with open('valid_shops_start_at_{start_id}.json'.format(start_id=start_id), 'w', encoding='utf-8') as save:
                log.error('导出数据ing...')
                json.dump(valid_shops, save, ensure_ascii=False, indent=2)
                log.error('导出数据成功')
        else:
            # log.error('没有新数据')
            pass

        with open('__start_id.json', 'w', encoding='utf-8') as ip_fp:
            json.dump(id, ip_fp)

        if len(valid_shops) >= batch_data_max_size:
            log.critical('本批次有效商铺数已超过%d，开始下一批次以减少json的dump的影响' % batch_data_max_size)
            start_id = id
            ban_cnt = 0
            valid_shops = []
            start_at = time.time()

        pass
    log.error('完成抓取')
    # 合并多次的结果，并添加地理信息
    merge_old_files_into_one_and_add_geo_info()


def get_start_id_from_file():
    try:
        with open('__start_id.json', 'r', encoding='utf-8') as ip_fp:
            start_id = json.load(ip_fp)
    except Exception:
        start_id = 0
    return start_id


def log_current_status(batch_size, id, last_res_cnt, loop_start_at, start_at, start_id, valid_shops):
    total_items_cnt = len(valid_shops)
    new_items_cnt = total_items_cnt - last_res_cnt
    new_items_rate = 100 * new_items_cnt / batch_size
    total_id = id - start_id
    total_items_rate = 100 * total_items_cnt / total_id
    loop_used = time.time() - loop_start_at
    total_used = time.time() - start_at
    req_uesd_avg = total_used / total_id
    loop_used_avg = 100 * req_uesd_avg
    ban_rate = 100 * ban_cnt / total_id
    log.error(
        '已连续抓取%d/%d(%.2f%%)个，导出目前已有数据%d/%d(%.2f%%)个，目前id为%d, 起始id为%d, 当前循环耗时%.2f(%.4f)秒，目前总计运行%.2f(%.4f)秒, 屏蔽次数%d/%d(%.2f%%)' % (
            new_items_cnt, batch_size, new_items_rate, total_items_cnt, total_id, total_items_rate, id, start_id,
            loop_used,
            loop_used_avg, total_used, req_uesd_avg, ban_cnt, total_id, ban_rate))


def merge_old_files_into_one_and_add_geo_info():
    import json
    import os
    import shutil
    from functools import reduce

    shop_filenames = [filename for filename in os.listdir('.') if filename.startswith('valid_shops_start_at_')]

    def get_records_in_file(file_name):
        with open(file_name, encoding='utf-8') as shops:
            return json.load(shops)

    # 从各个文件中获取数据，并将其合并
    items = reduce(lambda l1, l2: l1 + l2, map(get_records_in_file, shop_filenames))

    # 过滤掉无效的数据
    def is_valid_shop(shop):
        invalid = shop['name'] is None or shop['longitude'] is None or shop['address'] is None or shop[
                                                                                                      'latitude'] is None
        return not invalid

    items = filter(is_valid_shop, items)
    items = list(items)

    # 过滤掉重复的数据
    processed = set()

    def is_duplicated(shop):
        if shop['id'] in processed:
            return False
        else:
            processed.add(shop['id'])
            return True

    unique_items = filter(is_duplicated, items)
    unique_items = list(unique_items)

    duplicated_cnt = len(list(items)) - len(unique_items)
    print('重复ID个数: ', duplicated_cnt)

    total_ids = len(unique_items)
    # total_range = unique_items[-1].get('id', 0)
    total_range = max(unique_items, key=lambda item: item.get('id', 0)).get('id', 0)

    rate = total_ids / total_range
    print('总计:       ', total_ids)
    print('遍历至:     ', total_range)
    print('有效ID比率: ', rate)

    # 添加城市信息（city_id and formatted_address)
    print('添加地理信息ing')
    _session = requests.session()
    from multiprocessing.dummy import Pool as ThreadPool
    pool = ThreadPool(8)
    processed_status = {
        'ran_cnt': 0,
        'skipped_cnt': 0,
        'banned': False,
        'banned_cnt': 0
    }

    def fetch_cityid_and_formatted_address(item):
        if 'city_code' in item:
            processed_status['skipped_cnt'] += 1
        elif processed_status['banned']:
            processed_status['banned_cnt'] += 1
        else:
            api = 'http://api.map.baidu.com/geocoder/v2/'
            res = _session.get(api, params={
                'output': 'json',
                'ak': 'Eze6dPlb3bnUrihPNaaKljdUosb4G41B',
                'location': '{latitude},{longitude}'.format(latitude=item['latitude'], longitude=item['longitude']),
            }).json()
            if res['status'] != 0:
                processed_status['banned'] = True
                processed_status['banned_cnt'] = 1
                return fetch_cityid_and_formatted_address(item)
                pass
            res = res['result']
            item['city_code'] = res['cityCode']
            item['formatted_address'] = res['formatted_address']
            processed_status['ran_cnt'] += 1
        ran_cnt, skipped_cnt, banned_cnt = processed_status['ran_cnt'], processed_status['skipped_cnt'], processed_status['banned_cnt']
        cnt = ran_cnt + skipped_cnt

        print('\rran:%6d, skipped: %6d, banned: %6d/ total: %6d(%.2f%%)' % (ran_cnt, skipped_cnt, banned_cnt, total_ids, 100 * cnt / total_ids), end='', flush=True)

    pool.map(fetch_cityid_and_formatted_address, unique_items)
    print()

    # backup old files
    # check if backup directory exists
    import time
    backup_directory = '_old_files/{backuped_at}'.format(backuped_at=time.strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    print('将旧的文件移至备份区 @', backup_directory)
    for old_file in shop_filenames:
        shutil.move(old_file, os.path.join(backup_directory, old_file))

    # merge to one file
    saved_as = 'valid_shops_start_at_0_to_{max_id}@total_{total}.json'.format(max_id=total_range, total=total_ids)
    print('合并为一个文件 @ ', saved_as)
    with open(saved_as, 'w', encoding='utf-8') as save:
        json.dump(unique_items, save, ensure_ascii=False, indent=2)


def main():
    # TODO:
    # 1. 移除Shop等类，  只采用dict
    # 2. 将导出步骤分离出来
    # 3. 规范log


    # city = input('城市名: ')
    # brand = input('商家品牌名: ')
    # ids = input('商家ids：')
    city = ''
    brand = '周大虾龙虾盖浇饭'
    ids = '1468934, 1314141, 1214943, 1215005, 1314147, 1314153, 1314143, 1314146, 1215087, 1214907, 1314151, 1797366, 1357350, 1215053, 1447024, 1215012, 1215019'
    #
    crawler = MeituanCrawler()
    # 将两种整合到一起
    wb, saved_file = crawler.run_eleme(city, brand, ids)
    wb.save(saved_file)


if __name__ == '__main__':
    # FIXME: 美团的./backend/meituan_crawer.py in parse_urls line:354 进行屏蔽（404）休眠后重试
    # TODO: 提取类（url_fetcher, page_parser, item_exporter)，并设计各类职责，以及类的结构（继承与接口）
    # TODO: 提取各种设置到单独的类中
    # TODO：添加前端接口
    # timer(main)
    timer(get_eleme_ids)
    # timer(merge_old_files_into_one_and_add_geo_info)
    pass
