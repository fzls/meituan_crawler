#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json


def is_what_we_want(shop):
    return '盒马' in shop['name']
    # return shop['name'] is None or shop['longitude'] is None or shop['address'] is None or shop['latitude'] is None
    pass


if __name__ == '__main__':
    with open('valid_shops.json', encoding='utf-8') as data:
        shops = json.load(data)

        res = list(filter(is_what_we_want, shops))
        pass