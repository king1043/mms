# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
from db.elastic_search import ES

es = ES()

def set_mapping():
    mapping = {
        "tab_mms_net_program_v2018-03-10":{
            "settings" : {
              "number_of_shards" : 3,
              "number_of_replicas" : 1
              # "max_result_window": 10000 #设置返回的最大条数，默认为10000
            },
            "properties": {
                "total_play_count":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "episode":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "is_setmenu":{
                    "type":"long"
                },
                "keywords":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "program_name":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "net_source":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "score":{
                    "type":"float"
                },
                "release_year":{
                    "type":"date",
                    "format":"yyyy||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                },
                "actor":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "type":{
                    "type":"long"
                },
                "director":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "url":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "classify":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "rank":{
                    "type":"long"
                },
                "play_count_total":{
                    "type":"string"
                },
                "rank_wave":{
                    "type":"long"
                },
                "image_url":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "description":{
                    "type":"string",
                    "analyzer":"ik_max_word"
                },
                "create_time":{
                    "type":"date",
                    "format":"yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                },
                "program_id":{
                    "type":"string",
                    "index":"not_analyzed"
                },
                "sensitive":{
                    "type":"long"
                },
                "collect":{
                    "type":"long"
                },
                "institution":{
                    "type":"string",
                    "index":"not_analyzed"
                }
            }
        }
    }
    es.set_mapping('tab_mms_net_program_v2018-03-10', mapping)

if __name__ == '__main__':
    set_mapping()
    pass