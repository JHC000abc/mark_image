# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
desc: bos 相关操作
"""
import hashlib
import requests
import time
import json
import multiprocessing
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
from baidubce import utils


url_to_acquire_sts = 'http://liuxu19.atest.baidu.com/collection/api/getBosStsCredential'
bos_host = "https://bj.bcebos.com"
source_bucket = 'collection-data'

# access_key_id = "359794b9ccff4c03a01bdaaf0ede3be2"
# secret_access_key = "f078a60c30b94e18848a6008a58ac839"


def get_sts():
    """
    获取sts方法
    :return:
    """
    data = {
        'res': 3,
        'ct_user_id': 10020,
        'bucket': source_bucket,
        'permission': 'READ,WRITE',
        # 30分钟有效期
        'duration_seconds': 108000,
        'object': '*',
        'region': 'bj',
        'timestamp': int(time.time()),
    }
    data['sign'] = gen_sign(data)
    params = json.dumps(data)
    headers = {'Accept-Charset': 'utf-8', 'Content-Type': 'application/json'}
    res = requests.post(
        url=url_to_acquire_sts,
        data=params,
        headers=headers)

    # print(res.json())
    if res is None:
        raise AssertionError('request result is None')
    res = json.loads(res.text)
    if res['error_code'] > 0:
        msg = 'request result is error, error_code:' + \
            str(res['error_code']) + ', msg:' + res['msg']
        raise AssertionError(msg)
    return res['result']


def gen_sign(arr, key='sts'):
    """
    生成sts签名
    :return:
    """
    sorted_keys = sorted(arr.keys())

    raw_str = []
    for k in sorted_keys:
        raw_str.append(k + '=' + str(arr[k]))
    raw_str.append('key=' + key)
    md5 = hashlib.md5()
    md5.update('&'.join(raw_str).encode('utf8'))
    return md5.digest().hex()


def getBucketKey(url):
    """
    :param url:
    :return:
    """
    tmp_list = url.split('/')
    # 适配历史上由众测接口生成的下载文件
    if 'json-api/v1' in url:
        bucket = tmp_list[5]
        key = '/'.join(tmp_list[6:])
    elif tmp_list[2] in ['bd.bcebos.com', 'bj.bcebos.com']:
        bucket = tmp_list[3]
        key = '/'.join(tmp_list[4:])
    else:
        bucket = tmp_list[2].split('.')[0]
        key = '/'.join(tmp_list[3:])
    return bucket, key


def upload_file(bos_client,source_bucket, boss_file, local_file, status=0):
    """
    上传
    :param source_bucket: source_bucket = 'collection-data'
    :param boss_file: /jiaohaicheng/req_9233/1.jpg
    :param local_file:
    :param status:默认0 小文件上传，其他参数 支持分块上传
    :return:
    """
    if status == 0:
        res = bos_client.put_object_from_file(
            source_bucket, boss_file, local_file)
    else:
        res = bos_client.put_super_obejct_from_file(source_bucket, boss_file, local_file,
                                                    chunk_size=5, thread_num=multiprocessing.cpu_count(), progress_callback=utils.default_progress_callback)
    return res


def dowload_file(up_url, save_path, save_file_name):
    """
    下载
    :param up_url:完整的 url: http://collection-data.bj.bcebos.com/jiaohaicheng/test/1.jpg
    :param save_path:下载后的保存路径
    :param save_file_name: 下载后的问及那名
    :return:DownloadStatus
    """
    bucket, key = getBucketKey(up_url)
    save_file = os.path.join(save_path, save_file_name)
    res = bos_client.get_object_to_file(bucket, key, save_file)
    return res


def get_bos_client():
    """
    获取 bos_client
    :return: bos_client
    """
    sts = get_sts()
    access_key_id, secret_access_key, session_token = \
        sts["access_key_id"], sts["secret_access_key"], sts["session_token"]
    # 创建BceClientConfiguration
    config = BceClientConfiguration(
        credentials=BceCredentials(
            access_key_id,
            secret_access_key),
        endpoint=bos_host,
        # 使用sts方式，需携带 session_token
        security_token=session_token
    )
    bos_client = BosClient(config)
    return bos_client


if __name__ == '__main__':
    import os
    from Project.util import pathways_util

    bos_client = get_bos_client()

    # # 上传样例
    # local_path = R"D:\Desktop\aa"
    # for file in pathways_util.get_files_under_path(local_path):
    #     name = os.path.split(file)[-1]
    #     res = upload_file(
    #         source_bucket=source_bucket,
    #         boss_file="/jiaohaicheng/test2/{}".format(name),
    #         local_file=file,
    #         status=1)
    #     print(res)

    # # 下载样例
    # up_url = "https://bj.bcebos.com/collection-data/jiaohaicheng/test2/15_类型兼容性原则遇上还是函数重写_面向对象新需求.wmv"
    # save_path = R"D:\Desktop"
    # save_file_name = "15.mp4"
    # dowload_file(up_url, save_path, save_file_name)
