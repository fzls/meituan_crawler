import inspect
import json
import logging
import re
import time
import timeit
from functools import wraps
from random import randint
from urllib.parse import parse_qs, urlparse, urlencode

import requests
from bs4 import BeautifulSoup, Tag


def cached(func):
    # FIXME: use @pickle instead
    cache_file = 'cache.json'
    try:
        with open(cache_file, encoding='utf-8') as pers:
            func.cache = json.load(pers)
    except FileNotFoundError as e:
        func.cache = {}

    @wraps(func)
    def wrapper(*args):
        try:
            return func.cache[str(args)]
        except KeyError:
            func.cache[str(args)] = result = func(*args)
            with open(cache_file, 'w') as pers:
                json.dump(func.cache, pers, ensure_ascii=False, indent=2)
            return result

    return wrapper


# 设置时间格式
DATE_TIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

# logging.basicConfig(format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
logging.basicConfig(format='%(levelname)s [line:%(lineno)d] %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

dashes = '-' * 50


def eye_catching_logging(msg=''):
    log.debug('%s %s %s' % (dashes, msg.title(), dashes))


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

meituan_waimai_url = 'http://waimai.meituan.com'

headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    "Accept": "*/*",
    "DNT": "1",
    "Referer": "http://waimai.meituan.com/?stay=1",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en,zh-CN;q=0.8,zh;q=0.6,zh-TW;q=0.4,en-GB;q=0.2,ja;q=0.2",
    "Cookie": "BAIDUID=5365A55222D580D81C224BB2827B9BBD:FG=1; PSTM=1488433005; BIDUPSID=31FB76D71AEF46DDEDAB7059DACCD5B6; BDUSS=mpZeEQybW9uTzlmRUowTEl0UnlXQ3FtMWdWSHFlV0s2OGVGdHE5QUpGM1NtLXRZSVFBQUFBJCQAAAAAAAAAAAEAAAAx-PUbt-fWrsHo6eQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANIOxFjSDsRYc; cflag=15%3A3",
}

session = requests.session()
session.headers = headers

data_dir = '.'


# FIXME: add  JSON serializable support
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

    def __str__(self):
        # TODO: google it for if it can strify automatically
        return 'name: %s, address: %s, lat: %s, lng: %s, geo_hash: %s, url: %s' % (
            self.name, self.address, self.lat, self.lng, self.geo_hash, self.urls)



def _export_header_to_csv(column_names, save, seperator):
    save.write('{header}\n'.format(header=seperator.join(column_names)))
    pass


def _export_item_to_csv(column_names, item, save, seperator):
    line = []
    for cn in column_names:
        if item[cn] is not None:
            line.append(str(item[cn]))
        else:
            line.append('')
    save.write('{record}\n'.format(record=seperator.join(line)))
    pass


def export_one_to_csv(parsed_info: list, unique_file_name: str, seperator=','):
    filename = '{filename}.csv'.format(filename=unique_file_name)

    with open(filename, 'w', encoding='utf-8-sig') as save:
        if len(parsed_info) == 0:
            save.write('\n')
            return

        # 提取列名
        cns = parsed_info[0].keys()

        # 输出列名
        _export_header_to_csv(cns, save, seperator)

        # 将数据一行行写入文件
        for item in parsed_info:
            _export_item_to_csv(cns, item, save, seperator)

        log.eye_catching_logging('成功导出为{filename}'.format(filename=filename))
    pass


def export_one_shop(parsed_info, unique_file_name):
    log.eye_catching_logging('开始准备导出{filename}'.format(filename=unique_file_name))
    export_one_to_csv(parsed_info, unique_file_name)
    log.eye_catching_logging('完成导出{filename}'.format(filename=unique_file_name))
    log.debug('')
    pass


def get_filename_with_base_dir_prefix(filename):
    return '{data_dir}/{filename}'.format(data_dir=data_dir, filename=filename)


def parse_shop_page(shop: Shop):
    parsed_infos = []

    for idx, shop_url in enumerate(shop.urls):
        res = session.get(shop_url)

        soup = BeautifulSoup(res.text, 'lxml')

        # 获取基本信息
        food_data_nodes = soup.find_all('script', {'type': 'text/template', 'id': re.compile('foodcontext-\d+')})

        # log.debug(json.dumps([json.loads(food_data_node.string) for food_data_node in food_data_nodes], ensure_ascii=False, indent=2))

        parsed_info = []
        for food_data_node in food_data_nodes:  # type: Tag
            # TODO: add class product
            food = json.loads(food_data_node.string)
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

        shop_unique_name = '{shop_address}'.format(shop_name=shop.name,
                                                   shop_address=shop.address.replace('$', ''))
        if idx > 0:
            shop_unique_name += '_{index}'.format(index=idx)
        shop_unique_name += '_商品信息'

        unique_file_name = get_filename_with_base_dir_prefix(shop_unique_name)
        # 将当前商家导出到单独的csv
        export_one_shop(parsed_info, unique_file_name)

    return parsed_infos


def is_shop_in_this_city(address: str, shop_name: str, city_name: str):
    return shop_name in address and city_name in address


def find_possiable_addresses(cid_name: CityIdName, shop_name: str):
    bdmap_find_address_by_name_api = 'http://map.baidu.com/su'
    result_number = '65'

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
        if not is_shop_in_this_city(address, shop_name, cid_name.name):
            continue
        addresses.append(address)

    log.eye_catching_logging('api response for %s' % cid_name)
    log.debug(json.dumps(json_res, ensure_ascii=False, indent=2))

    log.eye_catching_logging('%s' % cid_name)
    log.list_debug(addresses)
    log.eye_catching_logging('total %s' % (len(addresses)))

    return addresses


def get_city_id_and_name(city_name: str):
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
                log.debug(city_id_name)

                return CityIdName(*city_id_name)

        log.info('%s not found in city list' % city_name)
        return [0, 'not found']


def add_lng_lat_by_address(addresses: list, shop_name=''):
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


def get_url_by_geo_hash_and_name(shop: Shop):
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

    for res_li in res_lis:
        res_name = res_li.find('p', {'class': 'name'}).string.replace('\n', '').strip()
        res_path = res_li.find('a')['href']

        # 检查该搜索结果是否为我们想要的结果 ： 看品牌名是否在搜索结果的标题中
        if is_the_shop_we_want(res_name, shop.name):
            log.debug('SUCCESSED in finding url in : {search_url}'.format(search_url=meituan_search_api))
            log.debug("result shop name is : %s" % res_name)
            log.debug("result shop path is : %s" % res_path)

            if res_path:
                shop_url = '{host}{path}'.format(host=meituan_waimai_url, path=res_path)
                shop.urls.append(shop_url)

                log.debug('url is : {url}'.format(url=shop_url))

    # log.debug(shop)
    pass


def fetch_geo_hash_for_shops(shops: list):
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


def timer(func, *args, **kwargs):
    ran_time = timeit.timeit(func, number=1)

    log.debug('method %s run %s seconds' % (func, ran_time))


def batch_get_url_by_geo_hash_and_name(shops):
    for shop in shops:
        if shop.geo_hash:
            get_url_by_geo_hash_and_name(shop)


def get_shops_exists_in_meituan(shops):
    filtered = list(filter(lambda shop: shop.urls, shops))

    log.eye_catching_logging('美团上该品牌开设{number_of_shop}家的店面如下所示'.format(number_of_shop=len(filtered)))
    log.list_debug(filtered)

    return filtered


def export_all_to_csv(parsed_infos: dict, unique_file_name: str, seperator=','):
    """

    :param parsed_infos: ex. {
        'shop_a': [
            {food_1},
            {food_2},
            {food_3},
        ],
        'shop_b': [
            {food_4},
            {food_5},
            {food_6},
        ],
    }

    :param filename:
    :return:
    """
    filename = '{filename}.csv'.format(filename=unique_file_name)

    with open(filename, 'w', encoding='utf-8-sig') as save:
        if len(parsed_infos) == 0:
            save.write('\n')
            return

        # 提取列名
        SHOP_NAME = '_shop_name'
        cns = [SHOP_NAME]
        # 提取商店内商品的列名，并附加到列名集合中
        cns += list(parsed_infos.values())[0][0].keys()

        # 排列列名保证每次输出一致
        cns = sorted(cns)

        # 输出列名
        _export_header_to_csv(cns, save, seperator)

        for shop_name, parsed_info in parsed_infos.items():
            for food in parsed_info:
                # 添加商店名信息
                food[SHOP_NAME] = shop_name

                # 将数据一行行写入文件
                _export_item_to_csv(cns, food, save, seperator)
            pass

        log.eye_catching_logging('成功导出为{filename}'.format(filename=filename))
    pass


def export_all_shops(parsed_infos: dict, filename):
    """

    :param parsed_infos: ex. {
        'shop_a': [
            {food_1},
            {food_2},
            {food_3},
        ],
        'shop_b': [
            {food_4},
            {food_5},
            {food_6},
        ],
    }

    :param filename:
    :return:
    """
    log.eye_catching_logging('开始准备导出{filename}'.format(filename=filename))
    export_all_to_csv(parsed_infos, filename)
    log.eye_catching_logging('完成导出{filename}'.format(filename=filename))
    log.debug('')
    pass


def parse_shops_and_export(shops: list):
    if len(shops) == 0:
        log.eye_catching_logging('商家列表为空')
        return
    log.eye_catching_logging('开始解析商家页面')

    parsed_infos = {}
    for shop in shops:
        for idx, parsed_info in enumerate(parse_shop_page(shop)):
            shop_unique_name = shop.address.replace('$', '')
            if idx > 0:
                shop_unique_name += '_{index}'.format(index=idx)

            parsed_infos[shop_unique_name] = parsed_info

    # log.json_debug(parsed_infos)

    # 将本次获取的商家信息导出到单个汇总的
    shop_name = shops[0].name
    filepath = '{shop_name}_商品信息_汇总'.format(shop_name=shop_name)
    export_all_shops(parsed_infos, get_filename_with_base_dir_prefix(filepath))

    return parsed_infos


def extract_urls(shops: list):
    urls = []
    for shop in shops:
        urls += shop.urls

    log.eye_catching_logging('提取url列表')
    log.list_debug(urls)

    return urls
    pass


def remove_duplicate_urls(shops):
    visited_urls = {}
    for shop in shops:
        urls = []
        for url in shop.urls:
            if not visited_urls.get(url):
                urls.append(url)
                visited_urls[url] = True

        # TODO: check if empty when use it
        shop.urls = urls
        pass

    return shops


def run_crawler_and_export(city_name, shop_name):
    global data_dir
    # 确保数据文件夹已创建
    import os
    data_dir = './{shopname}/{time}'.format(shopname=shop_name, time=time.strftime(DATE_TIME_FORMAT))
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    shops_exists_in_meituan = collect_shop_urls(city_name, shop_name)
    # TODO: 添加缓存 {已搜索过的关键词对} 机制（google一下，看Python有没有缓存库）
    parse_shops_info = parse_shops_and_export(shops_exists_in_meituan)


@cached
def collect_shop_urls(city_name, shop_name):
    # 处理逻辑
    cid_name = get_city_id_and_name(city_name)
    addresses = find_possiable_addresses(cid_name, shop_name)
    shops = add_lng_lat_by_address(addresses, shop_name)
    fetch_geo_hash_for_shops(shops)
    batch_get_url_by_geo_hash_and_name(shops)
    shops_exists_in_meituan = get_shops_exists_in_meituan(shops)
    # 对所有的url进行去重
    shops_exists_in_meituan = remove_duplicate_urls(shops_exists_in_meituan)
    return shops_exists_in_meituan


def main():
    # 1. 获取url
    # 2. 爬取内容
    # TODO： 3. 开发前端: 试试用Python写GUI
    # TODO:  4. 添加缓存机制（json, sqlite, yaml)
    city_name = '湛江'
    shop_name = '美优乐'
    # city_name = '杭州'
    # shop_name = '沙县小吃'

    run_crawler_and_export(city_name, shop_name)


def is_the_shop_we_want(res_name, shop_name):
    return shop_name in res_name


def test_get_shop_in_search_result():
    meituan_search_api = 'http://waimai.meituan.com/search/wtmkkyg0wq1b/rt?keyword=%E6%B1%87%E9%91%AB%E5%B0%8F%E5%90%83'
    res = session.get(meituan_search_api)
    shop_name = '汇鑫小吃'

    soup = BeautifulSoup(res.text, 'lxml')

    res_lis = soup.find_all('li', {'class': 'rest-list'})
    for res_li in res_lis:
        res_name = res_li.find('p', {'class': 'name'}).string.replace('\n', '').strip()
        res_path = res_li.find('a')['href']

        if is_the_shop_we_want(res_name, shop_name):
            print(res_name, res_path)


@cached
def test_cache(m):
    t = 0
    for i in range(1, m):
        t = t + t / i + i
    return t


if __name__ == '__main__':
    timer(main)
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
