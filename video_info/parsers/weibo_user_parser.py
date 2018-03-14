import sys
sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import video_info.parsers.base_parser as self_base_parser
import utils.tools as tools
from utils.log import log
from db.oracledb import OracleDB

SITE_ID = 2
NAME = '新浪微博'
db = OracleDB()

@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    site_id = SITE_ID
    name = NAME
    table = 'WWA_site_info'
    url = 'https://m.weibo.cn/'
    domain = 'weibo.cn'
    ip = '180.149.153.216'
    address = '中国 北京'
    base_parser.add_website_info(table, site_id, url, name, domain, ip, address)

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params):
    log.debug('''
        添加根url
        parser_params : %s
        ''' % str(parser_params))

    for program in parser_params: #[[91, '山东卫视', '调查', '新闻'], [...]]
        program_id = program[0]
        chan_name = program[1]
        program_name = program[2]
        program_type = program[3]
        image_url = program[4]
        is_have_official_blog = program[5]
        if is_have_official_blog == 2:
            search_keyword = tools.quote(chan_name + ' ' +program_name, safe='/:?=&%')
            url = 'http://m.weibo.cn/api/container/getIndex?type=user&containerid=100103type%3D3%26q%3D' + search_keyword
            base_parser.add_url('mms_urls', SITE_ID, url, remark = {'program_id' : program_id, 'chan_name' : chan_name, 'program_name' : program_name})


def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    program_id = url_info['remark']['program_id']
    program_name = url_info['remark']['program_name']
    chan_name = url_info['remark']['chan_name']

    is_continue = True

    for i in range(1, 2): # 只取了第一页
        if not is_continue: break

        list_url = root_url + '&page=%d' % i
        html = tools.get_json_by_requests(list_url)

        cards = html.get('data', {}).get('cards')
        card_group = []
        for i in cards:
            card_group = tools.get_json_value(i, 'card_group')
            if card_group:
                break
        if not card_group:
            break

        for info in card_group:
            user_info = tools.get_json_value(info, 'user')
            user_id = tools.get_json_value(user_info, 'id')

            user_url = 'http://m.weibo.cn/api/container/getIndex?containerid=230283%s_-_INFO' % user_id
            user_url_html = tools.get_json_by_requests(user_url)
            user_url_cards = tools.get_json_value(user_url_html, 'data.cards')
            user_url_card_group = tools.get_json_value(user_url_cards[0], 'card_group')
            area = ''
            for i in user_url_card_group:
                if tools.get_json_value(i, 'item_name') == '所在地':
                    area = tools.get_json_value(i, 'item_content')
                else:
                    continue

            name = tools.get_json_value(user_info, 'screen_name')
            verified_reason = tools.get_json_value(user_info, 'verified_reason')

            is_verified = 0
            if verified_reason: is_verified = 1

            sex = tools.get_json_value(user_info, 'gender')
            if sex == 'f':
                sex = 1
            elif sex == 'm':
                sex = 0
            else:
                sex = ''

            image_url = tools.get_json_value(user_info, 'profile_image_url')
            url = tools.get_json_value(user_info, 'profile_url')
            summary = tools.get_json_value(user_info, 'description')
            user_url_2 = 'http://m.weibo.cn/api/container/getIndex?containerid=100505%s' % user_id
            user_url_html_2 = tools.get_json_by_requests(user_url_2)
            fans_count = tools.get_json_value(user_url_html_2, 'userInfo.followers_count')
            follow_count = tools.get_json_value(user_url_html_2, 'userInfo.follow_count')

            log.debug('''
                节目id：     %s
                用户id：     %s
                微博昵称：   %s
                微博地址：   %s
                头像地址：   %s
                微博认证：   %s
                是否认证：   %s
                所在地：     %s
                性别：       %s
                简介：       %s
                粉丝数：     %s
                关注数：     %s
                ''' % (program_id, user_id, name, url, image_url, verified_reason, is_verified, area, sex,
                   summary, fans_count, follow_count))

            if program_name in name or program_name in verified_reason: # 搜索到想搜的用戶 不往下進行
                self_base_parser.add_weibo_user(program_id, user_id, name, url, image_url, verified_reason, is_verified, area, sex,
                   summary, fans_count, follow_count)

                # 更新 是否有官博字段
                sql = 'update TAB_MMS_PROGRAM set official_blog = 1 where program_id = %d'%program_id
                db.update(sql)

                is_continue = False
                break

    if is_continue:
        # 更新 是否有官博字段
        sql = 'update TAB_MMS_PROGRAM set official_blog = 0 where program_id = %d'%program_id
        db.update(sql)

    base_parser.update_url('mms_urls', root_url, Constance.DONE)

if __name__ == '__main__':
    url_info =  {'url': 'http://m.weibo.cn/api/container/getIndex?type=user&containerid=100103type%3D3%26q%3D%E5%B1%B1%E4%B8%9C%E5%8D%AB%E8%A7%86%20%E5%9B%BD%E5%AD%A6%E5%B0%8F%E5%90%8D%E5%A3%AB', 'status': 0, 'depth': 0, 'site_id': 2, 'remark': {'program_name': '国学小名士', 'program_id': 95, 'chan_name': '山东卫视'}, '_id': '5aa8e5f75344652c6ccd053e', 'retry_times': 0}
    parser(url_info)