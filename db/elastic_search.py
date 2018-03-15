# -*- coding: utf-8 -*-
'''
Created on 2017-08-22 14:06
---------
@summary: 同步oracle数据库到ElasticSearc
---------
@author: Boris
'''

import sys
sys.path.append('../')
import init
import utils.tools as tools
from elasticsearch import Elasticsearch
from utils.log import log

ADDRESS = tools.get_conf_value('config.conf', 'elasticsearch', 'address')

class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,'_inst'):
            cls._inst=super(Singleton,cls).__new__(cls)

        return cls._inst

class ES(Singleton):
    def __init__(self, address = ADDRESS):
        super(ES, self).__init__()
        if not hasattr(self,'_es'):
            try:
                self._es = Elasticsearch(address.split(','))
            except Exception as e:
                raise
            else:
                log.debug('连接到Elasticsearch')

    def add(self, table, data, data_id = None, doc_type = ''):
        '''
        @summary:
        ---------
        @param table: 索引
        @param data_json: 数据 json类型
        @param doc_type: 类型 空时以表命名。 doc_type可理解为同样的数据结构不同意意义。比如url表，doc_type 可以以网站名命名
        @param data_id data_id不指定，会自己创建， data_id已存在，则更新
        ---------
        @result:
        '''
        try:
            table = table.lower()
            self._es.index(index = table, doc_type = doc_type or table ,id = data_id, body = data)
        except Exception as e:
            log.error(e)
            return False
        else:
            return True

    def get(self, table, data_id, doc_type = '_all'):
        '''
        @summary: 根据id取数据
        ---------
        @param table:索引
        @param data_id:数据id 如 ID=1 的数据
        @param doc_type:类型 _all 为全部
        ---------
        @result: json
        '''
        datas = {}

        try:
            table = table.lower()
            datas = self._es.get(index = table, doc_type = doc_type, id = data_id)

        except Exception as e:
            # log.error(e)
            pass

        return datas


    def search(self, table, body = {}):
        '''
        @summary:
        ---------
        @param table:
        @param body: 查询条件
        ---------
        @result: json
        '''

        datas = {}

        try:
            table = table.lower()
            datas = self._es.search(index = table, body = body)

        except Exception as e:
            log.error(e)

        return datas

    def update_by_id(self, table, data_id, data, doc_type = ''):
        '''
        @summary:
        ---------
        @param table:
        @param data_id:
        @param data: {"TITLE":"xxx"} 更新的字段及值
        @param doc_type:
        ---------
        @result:
        '''


        self._es.update(index = table, doc_type = doc_type or table, body = {"doc": data}, id = data_id)

    def delete_by_id(self, table, data_id, doc_type = ''):
        """
        根据给定的id,删除文档
        :return:
        """
        self._es.delete(index = table, doc_type = doc_type or table, id = data_id)

    def set_mapping(self, table, mapping, doc_type = ''):
        '''
        @summary:
        ---------
        @param table:
        @param mapping:
        mapping = {
            doc_type: {
                "properties": {
                    "document_id": {
                        "type": "integer"
                    },
                    "title": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                }
            }
        }
        @param doc_type:
        ---------
        @result:
        '''

        if not self._es.indices.exists(index = table):
            # 创建Index和mapping
            self._es.indices.create(index = table, body = mapping, ignore=400)
            self._es.indices.put_mapping(index = table, doc_type = doc_type or table, body = mapping)

if __name__ == '__main__':
    es = ES()
    program ={
    "sensitive": 0,
    "rank": "1",
    "collect": 0,
    "total_play_count": "6亿播放",
    "net_source": "爱奇艺",
    "actor": "刘烨,林依晨,雷佳音,胡先煦,郭姝彤,李建义,王妍之",
    "keywords": "刘烨林依晨绝处逢爱",
    "url": "http://www.iqiyi.com/a_19rrh7t9vx.html",
    "episode": "更新至18集",
    "up_count": None,
    "director": "刘俊杰",
    "is_setmenu": 0,
    "baidu_score": None,
    "image_url": "http://pic4.qiyipic.com/image/20180305/0b/54/a_100055528_m_601_m6_180_101.jpg",
    "classify": "都市",
    "release_year": "2018",
    "rank_wave": 0,
    "program_id": "207680801",
    "record_time": "2018-03-15 11:05:58",
    "institution": "湖南卫视",
    "program_name": "老男孩",
    "description": "吴争，民航机长，拥有令人艳羡的职业和外型，飞行中他技术过硬，承载无数乘客的责任。生活中他天性不羁爱自由，恣意挥洒，不管他人眼光。在自己的世界里，做个彻头彻尾的老男孩。直到有一天，一个 16岁的儿子从天而降，一个正义的女老师林小欧紧随其后，两人前后脚的到来，彻底颠覆了吴争既有的生活。林小欧，无忧无虑的乐天派，时髦得有点用力，正义得有点莽撞，她是学生们亲切的姐姐、爽朗的朋友和没架子的好老师。当得知得意门生萧晗突遭家变，成了无家可归的孤儿，她费劲心力要与孩子生父沟通，当她见到了孩子生父才发现，原来，他就是自己不久前海外旅行时的噩梦——处处和她作对、极不靠谱的吴争 。",
    "play_count_total": "1.2亿",
    "score": "7.1",
    "type": 13
    }
    es.add('tab_mms_net_program', program, '207680801')
