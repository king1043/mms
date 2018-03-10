import sys
sys.path.append('../../')

import base.base_parser as base_parser
import video_info.parsers.base_parser as self_base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
# print(article_extractor.article_extractor)
# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '爱奇艺'

# 必须定义 添加网站信息
@tools.run_safe_model(__name__)
def add_site_info():
    log.debug('添加网站信息')
    pass

# 必须定义 添加根url
@tools.run_safe_model(__name__)
def add_root_url(parser_params = {}):
    log.debug('''
        添加根url
        parser_params : %s
        '''%str(parser_params))

    # 电视剧
    url = 'http://top.iqiyi.com/dianshiju.html'
    base_parser.add_url('mms_urls', SITE_ID, url)

# 必须定义 解析网址
def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    depth = url_info['depth']
    site_id = url_info['site_id']
    remark = url_info['remark']

    html, r = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('mms_urls', root_url, Constance.EXCEPTION)
        return

    # 榜单页提取排名等信息
    regex = '<i class="array\d?">(.*?)</i>.*?<em class="(.*?)">.*?<a href="(.*?)".*?title="(.*?)".*?data-aid="(.*?)".*?<img.*?"(http.*?)".*?<h3>(.*?)</h3>.*?<em class="mr15">(.*?)</em>.*?<em>(.*?)</em>'

    video_infos = tools.get_info(html, regex)
    for video_info in video_infos:
        rank = video_info[0]
        rank_wave = video_info[1] == 'trend-down' and -1 or video_info[1] == 'trend-up' and 1 or 0
        url = video_info[2]
        name = video_info[3]
        video_id = video_info[4]
        image_url = video_info[5]
        mini_summary = video_info[6]
        episode_msg = video_info[7]
        today_play_count = video_info[8]

        # 进详情页取详细信息
        html, r = tools.get_html_by_requests(url)
        # 总播放量
        regex = '<span class="effrct-PVNum">(.*?)</span>'
        total_play_count = tools.get_info(html, regex, fetch_one = True)

        regex = '<em>导演：.*?data-pb="2">(.*?)</a>'
        director = tools.get_info(html, regex, fetch_one = True)

        regex = '<em>类型：</em>.*?>(.*?)</a>'
        classify = tools.get_info(html, regex, fetch_one = True)

        regex = '<em>电视台：</em><span>(.*?)</span>'
        institution = tools.get_info(html, regex, fetch_one = True)

        regex = '<em class="ml50">年份：</em><a>(.*?)</a>'
        release_year = tools.get_info(html, regex, fetch_one = True)

        # 简介
        regex = 'data-moreorless="moreinfo".*?<span class="briefIntroTxt">(.*?)</span>'
        description = tools.get_info(html, regex, fetch_one = True)

        # 演员
        regex = '<div class="headImg-top">.*?<img title="(.*?)"'
        actor = tools.get_info(html, regex, split = ',')

        # 评分
        score_url = 'http://score-video.iqiyi.com/beaver-api/get_sns_score?qipu_ids={video_id}&appid=21&tvid={video_id}&pageNo=1'.format(video_id = video_id)
        html, r = tools.get_html_by_requests(score_url)
        regex = '"sns_score":(.*?)}'
        score = tools.get_info(html, regex, fetch_one = True)


        log.debug('''
            排名:       %s
            趋势：      %s
            url：       %s
            名称：      %s
            id：        %s
            贴图：      %s
            关键词：    %s
            集信息：    %s
            今日播放量：%s
            总播放量：  %s
            导演:       %s
            类型：      %s
            电视台：    %s
            年份：      %s
            简介：      %s
            演员:       %s
            评分：      %s
            '''%(rank, rank_wave, url, name, video_id, image_url, mini_summary, episode_msg, today_play_count, total_play_count, director, classify, institution, release_year, description, actor, score))

        self_base_parser.add_net_program(rank, rank_wave, url, name, video_id, image_url, mini_summary, episode_msg, today_play_count, total_play_count, director, classify, institution, release_year, description, actor, score, video_type = 2, net_source = '爱奇艺')

if __name__ == '__main__':
    url_info = {
        "remark": "",
        "_id": "5aa246f7534465166c0ce678",
        "retry_times": 0,
        "url": "http://top.iqiyi.com/dianshiju.html",
        "depth": 0,
        "status": 0,
        "site_id": 1
    }
    parser(url_info)
