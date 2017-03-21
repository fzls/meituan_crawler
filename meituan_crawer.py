#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import json
import logging
import re
import time
import timeit
from random import randint
from urllib.parse import parse_qs, urlparse, urlencode

import requests
import xlwt

ezxf = xlwt.easyxf

from bs4 import BeautifulSoup, Tag

### log 相关设置
# 设置时间格式
DATE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logging.basicConfig(format='%(asctime)s %(levelname)s [line:%(lineno)d] %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


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

            shop_unique_name = '{shop_name}@{shop_address}'.format(shop_name=shop_name,
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

    def parse_shops_and_export(self, shops: list, shop_name:str):
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

            res_total = self.get_striped_str(res_li.find('span', {'class': 'total'})).replace('月售','')
            res_start_price = self.get_striped_str(res_li.find('span', {'class': 'start-price'})).replace('起送','')

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

                    shop_in_res = Shop(res_name, shop.address,shop.lat, shop.lng,shop.geo_hash)
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

        res = session.get(bdmap_find_address_by_name_api, params=query)

        # print(test.status_code)
        res.encoding = 'utf-8'
        json_res = res.json()

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

    def run_crawler_and_export(self, city_name, shop_name):
        # 获取在该城市范围内该商店在美团上所开设的所有店铺的网址等信息
        shops_exists_in_meituan = self.collect_shop_urls(city_name, shop_name)

        # 对这些找到的店铺抓取其页面数据
        parse_shops_info = self.parse_shops_and_export(shops_exists_in_meituan, shop_name)

    def run(self, city_name='湛江', shop_name='美优乐'):
        """
        根据输入的城市名和商店名，找到该城市内该商店在美团所开设的所有店铺的商品的信息列表，并导出为xls文件
        :return:
        """
        # 1. 获取url
        # 2. 爬取内容
        #  3. 开发前端: 试试用Python写GUI
        # TODO:  4. 添加缓存机制（json, sqlite, yaml)
        ## 从用户获取城市和商店名
        # city_name = '湛江'
        # shop_name = '美优乐'

        log.eye_catching_logging('开始抓取[{city}]:[{shop}]'.format(city=city_name, shop=shop_name), log.error)
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


def timer(func, *args, **kwargs):
    ran_time = timeit.timeit(func, number=1)

    log.info('method %s run %s seconds' % (func, ran_time))


def main():
    # city = input('城市名: ')
    # name = input('商家名: ')
    #
    # wb, saved_file = run(city, name)
    crawler = MeituanCrawler()
    wb, saved_file = crawler.run()
    wb.save(saved_file)


if __name__ == '__main__':
    # timer(main)
    res = session.get('http://waimai.meituan.com/restaurant/144768513906661269')
    soup = BeautifulSoup(res.text, 'lxml')
    details_list = soup.select('div.details .list .na')[0]  # type: Tag
    shop_name = details_list.find_all('span')[0].string.strip()
    print(details_list.prettify())
    print(shop_name)


    # name = get_sheet_name('杭州\?%$123as-.,[]市江干区沙县小吃(中共闸弄口街道工作委员会西北)179_商品信息')
    # print(name)
    # wb.add_sheet(name)


    # import pickle
    # s = Shop('美优乐', '湛江市$廉江市$$美优乐(安铺店)', '21.460463270004844', '110.03258267897824', 'w7y4pfg23023', [
    #     'http://waimai.meituan.com/restaurant/144833350729852647'
    # ])
    # # with open('cache.pickle', 'wb') as save:
    # #     pickle.dump(s, save)
    #
    # with open('cache.pickle', 'rb') as save:
    #     s = pickle.load(save)
    #     print(type(s))
    #     print(s)
    # wb.add_sheet('这是一个_(测试)）（-')
    # timer(lambda:test_cache(10000000))
    # timer(lambda:test_cache(10000000))
    # timer(lambda:test_cache(10000000))
    # timer(lambda:test_cache(10000000))

    #
    # test_get_shop_in_search_result()

    #
    # parse_shops([Shop('美优乐', '湛江市$廉江市$$美优乐(安铺店)', '21.460463270004844', '110.03258267897824', 'w7y4pfg23023', [
    #     'http://waimai.meituan.com/restaurant/144833350729852647'
    # ])])

    # url = 'http://waimai.meituan.com/search/w7whgwwngrrc/rt'
    # params = {
    #     'keyword': '美优乐',
    #     'p2': 'test'
    # }
    # print(urlencode(params))
    # get_url_by_geo_hash_and_name(
    #     Shop('美优乐', '湛江市$廉江市$$美优乐(安铺店)', '21.460463270004844', '110.03258267897824', 'w7y4pfg23023'))
    #
    # meituan_search_api = 'http://waimai.meituan.com/search/{geo_hash}/rt?keyword={shop_name}'.format(geo_hash=123,
    #                                                                                                  shop_name=4213)
    #
    # print(meituan_search_api)
