# -*- coding: utf-8 -*-
'''
Created on 2017-01-03 11:05
---------
@summary: 提供一些操作数据库公用的方法
---------
@author: Boris
'''
import sys
sys.path.append('../../')
import init

import utils.tools as tools
from db.elastic_search import ES
# from db.mongodb import MongoDB

es = ES()
# mongodb = MongoDB()

def add_net_program(rank, rank_wave, url, name, video_id, image_url, mini_summary, episode_msg, today_play_count, total_play_count, director, classify, institution, release_year, description, actor, score, video_type, net_source):
    '''
    @summary:
    ---------
    @param rank:
    @param rank_wave:
    @param url:
    @param name:
    @param video_id:
    @param image_url:
    @param mini_summary:
    @param episode_msg:
    @param today_play_count:
    @param total_play_count:
    @param director:
    @param classify:
    @param institution:
    @param release_year:
    @param description:
    @param actor:
    @param score:
    @param type: 节目类型  电影 1 电视剧 2
    @param net_source: 来源 爱奇艺
    ---------
    @result:
    '''

    program = {
        'rank' : rank,
        'rank_wave' : rank_wave,
        'url' : url,
        'program_name' : name,
        'image_url' : image_url,
        'keywords' : mini_summary,
        'episode' : episode_msg,
        'play_count_total' : today_play_count,
        'total_play_count' : total_play_count,
        'director' : director,
        'classify' : classify,
        'institution' : institution,
        'release_year' : release_year,
        'description' : description,
        'actor' : actor,
        'score' : score,
        'type':video_type,
        'net_source':net_source,
        'create_time': tools.get_current_date(),
        'is_setmenu':0,
        'baidu_score': None,
        'up_count' : None,
        'collect':0,
        'sensitive':0,
        'program_id':video_id
    }

    es.add('tab_mms_net_program', program, video_id)