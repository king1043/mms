import sys
sys.path.append('../../')

import base.base_parser as base_parser
import video_info.parsers.base_parser as self_base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import random
# print(article_extractor.article_extractor)
# 必须定义 网站id
SITE_ID = 1
# 必须定义 网站名
NAME = '爱奇艺热点'

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

    if depth == 0:
        parser_video_info(root_url, depth, site_id, remark)

def parser_video_info(root_url, depth, site_id, remark):
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
        regex = ['data-moreorless="moreinfo".*?<span class="briefIntroTxt">(.*?)</span>', '<span class="briefIntroTxt">(.*?)</span>']
        description = tools.get_info(html, regex, fetch_one = True)

        # 演员
        regex = '<div class="headImg-top">.*?<img title="(.*?)"'
        actor = tools.get_info(html, regex, split = ',')

        # 评分
        score_url = 'http://score-video.iqiyi.com/beaver-api/get_sns_score?qipu_ids={video_id}&appid=21&tvid={video_id}&pageNo=1'.format(video_id = video_id)
        score_html, r = tools.get_html_by_requests(score_url)
        regex = '"sns_score":(.*?)}'
        score = tools.get_info(score_html, regex, fetch_one = True)


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

        self_base_parser.add_net_program(rank, rank_wave, url, name, video_id, image_url, mini_summary, episode_msg, today_play_count, total_play_count, director, classify, institution, release_year, description, actor, score, video_type = 13, net_source = '爱奇艺')

        parser_first_page_article(html, video_id, url)

        # 取wall_id, feed_id, sns_time
        regex = "\['wallId'\] = \"(.*?)\""
        wall_id = tools.get_info(html, regex, fetch_one = True)
        regex = "\['feedId'\] = (\d*?);"
        feed_id = tools.get_info(html, regex, fetch_one = True)
        regex = "\['snsTime'\] = (\d*?);"
        sns_time = tools.get_info(html, regex, fetch_one = True)
        parser_next_page_article(video_id, wall_id, feed_id, sns_time, url)
        # break

    base_parser.update_url('mms_urls', root_url, Constance.DONE)

def parser_first_page_article(html, video_id, url):
    regex = '(<div class="m-feedSection clearfix.*?)<!-- 评论列表 end-->'
    content_blocks = tools.get_info(html, regex)

    for content_block in content_blocks:
        regex = 'data-paopao-feedId="(.*?)"'
        article_id = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<img width="50".*?"(http.*?)"'
        head_url = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<a.*?data-paopao-ele="userUrl".*?title="(.*?)"'
        name = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<p class="feed_por_time">(.*?)</p>'
        release_time = tools.get_info(content_block, regex, fetch_one = True)
        release_time = tools.format_time(release_time)
        release_time = tools.format_date(release_time)

        regex = '<h3 class="title_icon_right" title="(.*?)">'
        title = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<span data-paopao-ele="dispalyContent.*?">(.*?)</span>'
        content = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<img width="100%" height="100%" data-lazy="(.*?)"'
        image_urls = tools.get_info(content_block, regex, split = ',')

        regex = '<em data-paopao-uvCnt=.*?>(.*?)</em>'
        watch_count = tools.get_info(content_block, regex, fetch_one = True)
        watch_count = tools.get_int(watch_count)

        regex = '<em data-paopao-agreeCnt="(.*?)">'
        up_count = tools.get_info(content_block, regex, fetch_one = True)

        regex = '<em data-paopao-commentCnt="(.*?)">'
        comment_count = tools.get_info(content_block, regex, fetch_one = True)

        log.debug('''
            id：       %s
            节目id     %s
            头像地址： %s
            名字：     %s
            发布时间： %s
            标题：     %s
            内容：     %s
            图片地址： %s
            观看量：   %s
            点赞量：   %s
            评论量：   %s
            '''%(article_id, video_id, head_url, name, release_time, title, content, image_urls, watch_count, up_count, comment_count))

        if self_base_parser.add_article(article_id, head_url, name, release_time, title, content, image_urls, watch_count, up_count, comment_count, program_id = video_id, gender = random.randint(0,1), url = url, info_type = 3, emotion = random.randint(0,2), collect = 0, source = '爱奇艺'):

            # 解析評論
            regex = "\['wallId'\] = \"(.*?)\""
            wall_id = tools.get_info(html, regex, fetch_one = True)
            parser_comment(article_id, wall_id)
        else:
            break

def parser_next_page_article(video_id, wall_id, feed_id, sns_time, url):
    article_json_url = 'http://api-t.iqiyi.com/feed/get_feeds?authcookie=&device_id=pc_web&m_device_id=a11e6ea94270eaaa0b46be30af84fc54&agenttype=118&wallId={wall_id}&feedTypes=1%2C7%2C8%2C9&count=20&top=1&hasRecomFeed=1&feedId={feed_id}&needTotal=1&notice=1&version=1&upOrDown=1&snsTime={sns_time}&_={timestamp_m}'.format(wall_id = wall_id, feed_id = feed_id, sns_time = sns_time, timestamp_m = int(tools.get_current_timestamp() * 1000))
    print(article_json_url)
    article_json = tools.get_json_by_requests(article_json_url)

    wall_id = article_json.get('data', {}).get('wallId')
    # 评论数组
    feeds = article_json.get('data', {}).get('feeds', [])
    for feed in feeds:
        article_id = feed.get('commentId')

        head_url = feed.get('icon')

        name = feed.get('name')

        release_time = feed.get('releaseDate')
        release_time = tools.timestamp_to_date(release_time)

        title = feed.get('feedTitle')

        content = feed.get('description')

        image_urls = ','.join([img.get('url') for img in feed.get('pictures', [])])#逗号分隔

        watch_count = feed.get('uvCount')

        up_count = feed.get('agreeCount')

        comment_count = feed.get('commentCount')

        log.debug('''
            id：       %s
            节目id     %s
            头像地址： %s
            名字：     %s
            发布时间： %s
            标题：     %s
            内容：     %s
            图片地址： %s
            观看量：   %s
            点赞量：   %s
            评论量：   %s
            '''%(article_id, video_id, head_url, name, release_time, title, content, image_urls, watch_count, up_count, comment_count))

        if self_base_parser.add_article(article_id, head_url, name, release_time, title, content, image_urls, watch_count, up_count, comment_count, program_id = video_id, gender = random.randint(0,1), url = url, info_type = 3, emotion = random.randint(0,2), collect = 0, source = '爱奇艺'):
            # 解析評論
            parser_comment(article_id, wall_id)
        else:
            break
    else:
        if feeds:
            feed_id = feeds[-1].get('feedId')
            sns_time = feeds[-1].get('snsTime')
            parser_next_page_article(video_id, wall_id, feed_id, sns_time, url)

def parser_comment(content_id, wall_id, page = 1):
    log.debug('正在爬取第 %s 页文章评论 content_id = %s'%(page, content_id))
    flow_comment_url = 'http://sns-comment.iqiyi.com/v2/comment/get_comments.action?contentid={content_id}&page={page}&authcookie=null&page_size=40&wallId={wall_id}&agenttype=117&t={timestamp_m}'.format(content_id = content_id, page = page, wall_id = wall_id, timestamp_m = int(tools.get_current_timestamp() * 1000))

    comment_json = tools.get_json_by_requests(flow_comment_url)
    data = comment_json.get('data', {})

    # 可作为翻页的依据
    total_count = data.get('totalCount', 0)
    count = data.get('count', 0)

    replies = data.get('replies', [])
    for reply in replies:
        reply_source = reply.get("replySource", {})
        if not deal_comment(reply_source):
            break

        if not deal_comment(reply):
            break

    else:
        if replies:
            parser_comment(content_id, wall_id, page + 1)

def deal_comment(reply):
    if not reply: return

    comment_id = reply.get('id')
    pre_id = reply.get('replyId')
    content = reply.get('content')
    article_id = reply.get('mainContentId')
    release_time = reply.get('addTime')
    release_time = tools.timestamp_to_date(release_time)
    head_url = reply.get('userInfo', {}).get('icon')
    consumer = reply.get('userInfo', {}).get('uname')
    gender = int(reply.get('userInfo', {}).get('gender'))
    up_count = reply.get('likes')

    # TODO
    emotion = random.randint(0, 2)
    hot_id =  comment_id

    log.debug('''
        评论id：  %s
        父id      %s
        文章id    %s
        发布人：  %s
        头像地址  %s
        性别      %s
        内容：    %s
        点赞量    %s
        发布时间  %s
        '''%(comment_id, pre_id, article_id, consumer, head_url, gender, content, up_count, release_time))

    return self_base_parser.add_comment(comment_id, pre_id, article_id, consumer, head_url, gender, content, up_count, release_time, emotion, hot_id)


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

    # 平论文章 第一页在原网页中 加载更多时请求如下地址
    # 最后一篇评论里的参数
    # wall_id = 235458347
    # feed_id = 82050174248
    # sns_time = 1520667435

    # comment_article_url = 'http://api-t.iqiyi.com/feed/get_feeds?authcookie=&device_id=pc_web&m_device_id=a11e6ea94270eaaa0b46be30af84fc54&agenttype=118&wallId={wall_id}&feedTypes=1%2C7%2C8%2C9&count=20&top=1&hasRecomFeed=1&feedId={feed_id}&needTotal=1&notice=1&version=1&upOrDown=1&snsTime={sns_time}&_={timestamp_m}'.format(wall_id = wall_id, feed_id = feed_id, sns_time = sns_time, timestamp_m = int(tools.get_current_timestamp() * 1000))

    # print(comment_article_url)


    # # 评论文章的评论 参数在文章中获取
    # content_id = 81180097548
    # wall_id =  ''
    # page = ''

    # flow_comment_url = 'http://sns-comment.iqiyi.com/v2/comment/get_comments.action?contentid={content_id}&page={page}&authcookie=null&page_size=40&wallId={wall_id}&agenttype=117&t={timestamp_m}'.format(content_id = content_id, page = page, wall_id = wall_id, timestamp_m = int(tools.get_current_timestamp() * 1000))
