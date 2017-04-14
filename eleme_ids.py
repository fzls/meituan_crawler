#!/usr/bin/env python
# -*- coding: utf-8 -*-

def merge_old_files_into_one():
    import json
    import os
    import shutil
    from functools import reduce

    shop_filenames = [filename for filename in os.listdir('.') if filename.startswith('valid_shops_start_at_')]

    def get_records_count_in_file(file_name):
        with open(file_name, encoding='utf-8') as shops:
            return len(json.load(shops))
        pass

    def get_records_max_id_in_file(file_name):
        with open(file_name, encoding='utf-8') as shops:
            return json.load(shops)[-1].get('id',0)
        pass

    def get_records_in_file(file_name):
        with open(file_name, encoding='utf-8') as shops:
            return json.load(shops)
        pass

    total_ids = reduce(lambda sum, cnt: sum + cnt, map(get_records_count_in_file, shop_filenames))
    total_range = reduce(lambda max_id, max_id_in_file: max(max_id, max_id_in_file), map(get_records_max_id_in_file, shop_filenames))
    items = reduce(lambda l1, l2: l1+l2, map(get_records_in_file, shop_filenames))
    def is_valid_shop(shop):
        invalid = shop['name'] is None or shop['longitude'] is None or shop['address'] is None or shop['latitude'] is None
        return not invalid

    items = list(filter(is_valid_shop, items))
    rate = total_ids / total_range
    print('总计:       ', total_ids)
    print('遍历至:     ', total_range)
    print('有效ID比率: ', rate)

    # backup old files
    # check if backup directory exists
    import time
    backup_directory = '_old_files/{backuped_at}'.format(backuped_at = time.strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(backup_directory):
        os.makedirs(backup_directory)

    print('将旧的文件移至备份区 @', backup_directory)
    for old_file in shop_filenames:
        shutil.move(old_file, os.path.join(backup_directory, old_file))

    # merge to one file
    print('合并为一个文件')
    with open('valid_shops_start_at_0_to_{max_id}@total_{total}.json'.format(max_id=total_range, total = total_ids), 'w', encoding='utf-8') as save:
        json.dump(items, save, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    # merge_old_files_into_one()
    import yaml
    with open('valid_shops_start_at_0_to_730895@total_121132.yaml', 'r', encoding='utf-8') as data:
    # with open('_old_files/2017-04-13_08-03-12/valid_shops_start_at_0_to_611197@total_91678.json', 'r', encoding='utf-8') as data:
        # yaml.dump(t, save)
        import time
        start = time.time()

        import sqlite3
        import json
        # shops = json.load(data)

        shops = yaml.load(data)
        print('loaded')
        cid = 289 # 上海
        brand = '沙县小吃'
        needed = filter(lambda shop: shop['city_code'] == cid and brand in shop['name'], shops)
        needed = list(needed)
        print('len', len(needed))
        print('first 10', needed[:10])
        print('uesd %.2fs'%(time.time() - start))

    pass