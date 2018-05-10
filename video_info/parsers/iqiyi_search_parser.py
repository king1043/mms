import sys
sys.path.append('../../')

import base.base_parser as base_parser
import video_info.parsers.base_parser as self_base_parser
import init
import utils.tools as tools
from utils.log import log
import base.constance as Constance
import random
from db.oracledb import OracleDB

# 必须定义 网站id
SITE_ID = 2
# 必须定义 网站名
NAME = '爱奇艺搜索'

db = OracleDB()

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

    for program in parser_params: #[[91, '山东卫视', '调查', '新闻'], [...]]
        program_id = program[0]
        chan_name = program[1]
        program_name = program[2]
        program_type = program[3]
        image_url = program[4]
        if program_type != '其他':
            url = 'http://so.iqiyi.com/so/q_%s %s?source=input&sr=1170053009947'%(program_name, program_type)
        else:
            url = 'http://so.iqiyi.com/so/q_%s?source=input&sr=1170053009947'%(program_name)
        base_parser.add_url('mms_urls', SITE_ID, url, remark = {'program_id':program_id, 'program_name':program_name, 'chan_name':chan_name, 'program_type':program_type, 'image_url':image_url})

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
    program_id = remark.get('program_id')
    chan_name = remark.get('chan_name')
    program_name = remark.get('program_name')
    program_type = remark.get('program_type')
    is_need_update = not remark.get('image_url') or False

    html, r = tools.get_html_by_requests(root_url)
    if not html:
        base_parser.update_url('mms_urls', root_url, Constance.EXCEPTION)
        return

    regex = '(<li class="list_item".*?</li>)'
    video_blocks = tools.get_info(html, regex)
    for video_block in video_blocks:
        regex = '<a class="figure  figure-180236.*?href="(.*?)"'
        url = tools.get_info(video_block, regex, fetch_one = True)

        regex = '<img width="140" height="187" alt="(.*?)"'
        name = tools.get_info(video_block, regex, fetch_one = True)

        if (not url) or (not program_name in name):
            continue

        regex = '<em class="fs12 c999">&nbsp;(.*?)</em>'
        release_year = tools.get_info(video_block, regex, fetch_one = True)

        regex = '<label class="result_info_lbl">.*?</label>[^<]*?<a data-searchpingback-elem="link.*?>(.*?)</a>'
        director = tools.get_info(video_block, regex, fetch_one = True)

        html = tools.get_html(url)

        # 节目类别
        regex = '<a href=.*?class="channelTag".*?>(.*?)</a>'
        video_type = tools.get_info(html, regex, fetch_one = True)

        # if program_type != '其他' and video_type and program_type != video_type:
        #     # print(video_type, name)
        #     continue

        regex = [
            '<div class="info-img">.*?<img src="(.*?)"',
            '<div class="result_pic pr" >.*?<img.*?src="(.*?)"'

        ]
        image_url = tools.get_info(html, regex, fetch_one = True)

        regex = '<em>导演：.*?"director">(.*?)</a>'
        director = director or tools.get_info(html, regex, fetch_one = True)

        regex = [
            '<p class="episodeIntro-time" itemprop="datePublished">.*?<span>(.*?)</span>'#,
            '<em class="ml50">年份：</em><a>(.*?)</a>',
            '<em>更新至.*?>(.*?)</a>'
        ]
        release_year = release_year or tools.get_info(html, regex, fetch_one = True)

        regex = '<em>类型.*?<a href.*?>(.*?)</a>'
        classify = tools.get_info(html, regex, fetch_one = True)

        regex = '<em>电视台：</em><span>(.*?)</span>'
        institution = tools.get_info(html, regex, fetch_one = True)

        # 简介
        regex = [
            'data-moreorless="moreinfo".*?<span class="briefIntroTxt">(.*?)</span>',
            '<span class="briefIntroTxt">(.*?)</span>',
            '<span class="showMoreText" data-moreorless="moreinfo".*?简介：</em>(.*?)</span>'
        ]
        description = tools.get_info(html, regex, fetch_one = True)

        # 演员
        regex = ['<div class="headImg-top">.*?<img title="(.*?)"', '<div class="headImg-top">.*?<img.*?alt="(.*?)"']
        actor = tools.get_info(html, regex, split = ',')

        # 節目id
        regex = 'data-score-tvid="(.*?)"'
        video_id = tools.get_info(html, regex, fetch_one = True)

        # 评分
        score_url = 'http://score-video.iqiyi.com/beaver-api/get_sns_score?qipu_ids={video_id}&appid=21&tvid={video_id}&pageNo=1'.format(video_id = video_id)
        score_html, r = tools.get_html_by_requests(score_url)
        regex = '"sns_score":(.*?)}'
        score = tools.get_info(score_html, regex, fetch_one = True)


        log.debug('''
            url：       %s
            名称：      %s
            id：        %s
            贴图：      %s
            导演:       %s
            节目类别    %s
            类型：      %s
            电视台：    %s
            年份：      %s
            简介：      %s
            演员:       %s
            评分：      %s
            '''%(url, name, video_id, image_url, director, video_type, classify, institution, release_year, description, actor, score))

        if is_need_update:
            sql = '''
                update tab_mms_program t set
                    t.image_url = '%s',
                    t.director = '%s',
                    t.description = '%s',
                    t.score = %s,
                    t.actor = '%s'
                where t.program_id = %d
            '''%(image_url, director, description, score, actor, program_id)
            print(sql)
            db.update(sql)

        # 评论区类评论http://www.iqiyi.com/a_19rrhcvhph.html
        parser_comment_article(html, video_id, program_id, url)
        # 剧情讨论http://www.iqiyi.com/a_19rrhebm2l.html
        parser_first_page_article(html, program_id, url)
        # 取wall_id, feed_id, sns_time 翻页
        regex = "\['wallId'\] = \"(.*?)\""
        wall_id = tools.get_info(html, regex, fetch_one = True)
        regex = "\['feedId'\] = (\d*?);"
        feed_id = tools.get_info(html, regex, fetch_one = True)
        regex = "\['snsTime'\] = (\d*?);"
        sns_time = tools.get_info(html, regex, fetch_one = True)
        if wall_id:
            parser_next_page_article(video_id, wall_id, feed_id, sns_time, url)
        break # 找到了想要查找到的节目， 后面的不继续爬取评论  跳出

    base_parser.update_url('mms_urls', root_url, Constance.DONE)


#########################################################
def parser_comment_article(html, video_id, program_id, url, page = 1):
    '''
    @summary: 评论区  如 http://www.iqiyi.com/a_19rrhcvhph.html
    ---------
    @param html:
    @param video_id:
    ---------
    @result:
    '''
    regex = 'data-qitancomment-tvid="(.*?)"'
    tvid = tools.get_info(html, regex, fetch_one = True)

    regex = 'data-qitancomment-qitanid="48970759"'
    aid = tools.get_info(html, regex, fetch_one = True)

    if not tvid and not aid:
        return

    comment_url = 'http://api-t.iqiyi.com/qx_api/comment/get_video_comments?aid={aid}&albumid={video_id}&categoryid=15&cb=fnsucc&escape=true&is_video_page=true&need_reply=true&need_subject=true&need_total=1&page={page}&page_size=10&page_size_reply=3&qitan_comment_type=1&qitanid={aid}&qypid=01010011010000000000&reply_sort=hot&sort=add_time&tvid={tvid}'.format(aid = aid, video_id = video_id, tvid = tvid, page = page)

    comment_json = tools.get_json_by_requests(comment_url)
    comments = comment_json.get('data', {}).get('comments', [])
    for comment in comments:
        article_id = comment.get('contentId')
        title = comment.get('title')
        content = comment.get('content')
        image_urls = None

        release_time = comment.get('addTime')
        release_time = tools.timestamp_to_date(release_time)

        up_count = comment.get('counterList',{}).get('likes')
        watch_count = comment.get('counterList', {}).get('reads')
        comment_count = comment.get('counterList', {}).get('replies')

        name = comment.get('userInfo', {}).get('uname')
        head_url = comment.get('userInfo', {}).get('icon')
        gender = int(comment.get('userInfo', {}).get('gender'))

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
            '''%(article_id, video_id, head_url, name, release_time, title, content, '', watch_count, up_count, comment_count))

        if self_base_parser.add_article(article_id, head_url, name, release_time, title, content, image_urls, watch_count, up_count, comment_count, program_id = program_id, gender = gender, url = url, info_type = 3, emotion = random.randint(0,2), collect = 0, source = '爱奇艺'):
            # 解析回复
            reply_list = comment.get('replyList') or []
            parser_relpy_comment(reply_list)
        else:
            break

    else:
        if comments:
            parser_comment_article(html, video_id, program_id, url, page + 1)

def parser_relpy_comment(reply_list):
    for reply in reply_list:
        comment_id = reply.get('id')
        pre_id = 0
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

        if not self_base_parser.add_comment(comment_id, pre_id, article_id, consumer, head_url, gender, content, up_count, release_time, emotion, hot_id):
            break

#########################################################

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
    url_info = {'status': 0, 'retry_times': 0, 'url': 'http://so.iqiyi.com/so/q_山东新闻联播 新闻?source=input&sr=1170053009947', 'depth': 0, '_id': '5af43adf53446526a0e781da', 'remark': {'chan_name': '山东卫视', 'program_id': 223, 'program_type': '新闻', 'image_url': 'http://pic0.qiyipic.com/image/20140604/ee/59/c7/li_30322_li_601_m1_180_236.jpg', 'program_name': '山东新闻联播'}, 'site_id': 2}
    parser(url_info)
