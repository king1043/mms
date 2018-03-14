import sys

sys.path.append('../../')

import init
import base.constance as Constance
import base.base_parser as base_parser
import utils.tools as tools
from utils.log import log
import datetime

SITE_ID = 10004
search_type = 102
NAME = '新浪微博'


FILE_LOCAL_PATH = tools.get_conf_value('config.conf', 'files', 'wwa_save_path') + 'weibo/'


def get_release_time(mblog):
    try:
        release_time = mblog['created_at']
        data = tools.time.time()
        ltime = tools.time.localtime(data)
        timeStr = tools.time.strftime("%Y-%m-%d", ltime)
        if tools.re.compile('今天').findall(release_time):
            release_time = release_time.replace('今天', '%s' % timeStr)
        elif tools.re.compile('昨天').findall(release_time):
            today = datetime.date.today()
            yesterday = today - datetime.timedelta(days=1)
            release_time = release_time.replace('昨天', '%s' % yesterday)
        elif '小时前' in release_time:
            nhours = tools.re.compile('(\d+)小时前').findall(release_time)
            hours_ago = (tools.datetime.datetime.now() - tools.datetime.timedelta(hours=int(nhours[0])))
            release_time = hours_ago.strftime("%Y-%m-%d %H:%M")
        elif tools.re.compile('分钟前').findall(release_time):
            nminutes = tools.re.compile('(\d+)分钟前').findall(release_time)
            minutes_ago = (tools.datetime.datetime.now() - tools.datetime.timedelta(minutes=int(nminutes[0])))
            release_time = minutes_ago.strftime("%Y-%m-%d %H:%M")
        elif tools.re.compile('刚刚').findall(release_time):
            release_time = tools.get_current_date()
        else:
            if len(release_time) < 10:
                release_time = '%s-%s' % (timeStr[0:4], release_time)
    except:
        release_time = ''
    finally:
        return release_time


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

    keywords_list = parser_params['result_list']
    for result in keywords_list:
        keywords = str(result[0]).split(',')

        for search_keyword in keywords:
            if not search_keyword:
                continue
            containerid = '230413' + search_keyword

            weibo_content_url = 'http://m.weibo.cn/api/container/getIndex?containerid=%s_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03' % containerid
            base_parser.add_url('WWA_weibo_info_urls', SITE_ID, weibo_content_url,
                                remark={'search_keyword': search_keyword})


def parser(url_info):
    url_info['_id'] = str(url_info['_id'])
    log.debug('处理 \n' + tools.dumps_json(url_info))

    root_url = url_info['url']
    weibo_id = url_info['remark']['search_keyword']

    page_count = 100

    for i in range(0, page_count + 1):
        weibo_content_url = root_url + '&page=%d' % i

        headers = {
            "Cache-Control": "max-age=0",
            "Cookie": "_T_WM=e0a91a3ed6286a67e649ce567fbbd17a; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D2304131560851875_-_WEIBO_SECOND_PROFILE_WEIBO%26fid%3D100103type%253D401%2526q%253D%26uicode%3D10000011",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Host": "m.weibo.cn",
            "Accept-Encoding": "gzip, deflate, br",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        }
        html = tools.get_json_by_requests(weibo_content_url, headers=headers)

        cards = tools.get_json_value(html, 'data.cards')
        if len(cards) < 2:
            base_parser.update_url('WWA_weibo_info_urls', root_url, Constance.DONE)
            return

        for card in cards:
            mblog = tools.get_json_value(card, 'mblog')
            if not mblog:
                continue

            url = tools.get_json_value(card, 'scheme')
            article_id = tools.get_json_value(mblog, 'id')
            article_url = 'https://m.weibo.cn/status/' + article_id

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Cookie": "_T_WM=e0a91a3ed6286a67e649ce567fbbd17a; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D100103type%253D401%2526q%253D%26fid%3D2304131560851875_-_WEIBO_SECOND_PROFILE_WEIBO%26uicode%3D10000011",
                "Host": "m.weibo.cn",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Upgrade-Insecure-Requests": "1",
                "Connection": "keep-alive"
            }
            origin_html, r = tools.get_html_by_requests(url, headers=headers)
            if not origin_html:
                continue

            # 精确到具体时分秒 需进入到article_url
            release_time = mblog['created_at']
            release_time = tools.format_time(release_time)
            # release_time = get_release_time(mblog)
            release_time = tools.format_date(release_time)

            come_from = tools.get_json_value(mblog, 'source')
            regexs = ['"text": "(.+?)",']
            content = ''.join(tools.get_info(origin_html, regexs))
            # content = tools.del_html_tag(content)
            content = content.replace('\\', '')

            regexs = ['"pic_ids": \[(.*?)\],']
            image_url = ''.join(tools.get_info(origin_html, regexs))
            image_url = tools.del_html_tag(image_url).replace('\"', '').replace('\\n', '')
            if image_url:
                image_url = image_url.split(',')
                for i in range(len(image_url)):
                    image_url[i] = 'http://wx2.sinaimg.cn/large/' + image_url[i] + '.jpg'

                image_url = ','.join(image_url)

            regexs = ['"stream_url": "(.*?)"']
            video_url = ''.join(tools.get_info(origin_html, regexs))
            transpond_count = tools.get_json_value(mblog, 'reposts_count')
            praise_count = tools.get_json_value(mblog, 'attitudes_count')
            comments_count = tools.get_json_value(mblog, 'comments_count')

            log.debug('''
                原文地址：     %s
                微博ID：       %s
                发布时间：     %s
                来自：         %s
                内容：         %s
                图片地址：     %s
                视频地址：     %s
                评论数：       %s
                转发数：       %s
                点赞数：       %s
                ''' % (article_url, weibo_id, release_time, come_from, content, image_url, video_url, comments_count,
                    transpond_count, praise_count))

            if comments_count > 0:
                parser_comment(article_id)


    base_parser.update_url('WWA_weibo_info_urls', root_url, Constance.DONE)

def parser_comment(article_id):
    page = 1
    while True:
        url = 'https://m.weibo.cn/api/comments/show?id=%s&page=%s'%(article_id, page)
        comment_json = tools.get_json_by_requests(url)
        msg = comment_json.get('msg')
        if msg == '暂无数据':
            break

        comment_datas = comment_json.get('data', {}).get('data', [])
        for comment_data in comment_datas:
            comment_id = comment_data.get('id')
            release_time = comment_data.get('created_at')
            release_time = tools.format_date(release_time)
            come_from = comment_data.get('source')
            content = comment_data.get('text')
            praise_count = comment_data.get('like_counts')
            user_name = comment_data.get('user', {}).get('screen_name')
            head_url = comment_data.get('user', {}).get('profile_image_url')

            log.debug('''
                id:       %s
                发布时间：%s
                来自：    %s
                内容：    %s
                点赞数：  %s
                用户名    %s
                头像地址  %s
                '''%(comment_id, release_time, come_from, content, praise_count, user_name, head_url))

        page += 1

if __name__ == '__main__':
    url_info = {
        "remark": {
            "search_keyword": "1615650934"
        },
        "site_id": 10004,
        "status": 0,
        "_id": "5a6705becdd76b0b0472ff1b",
        "url": "http://m.weibo.cn/api/container/getIndex?containerid=2304131615650934_-_WEIBO_SECOND_PROFILE_WEIBO&page_type=03",
        "retry_times": 0,
        "depth": 0
    }
    parser(url_info)