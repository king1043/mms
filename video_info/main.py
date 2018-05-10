import sys
sys.path.append('../')
import init
import pid
pid.record_pid(__file__)
import utils.tools as tools
from utils.log import log
from base.spider import Spider
from utils.export_data import ExportData
from db.oracledb import OracleDB

# 需配置
from video_info.parsers import *

def main():
    db = OracleDB()

    sql = '''
        select t.program_id, c.chan_name, program_name, d.name, t.image_url, t.official_blog
          from TAB_MMS_PROGRAM t
          left join tab_mam_chan c
            on c.chan_id = t.chan_id
          left join tab_mms_dictionary d
            on t.type = d.id
           and d.type = 2
    '''
          # where t.program_id =  226
    program_info = db.find(sql)

    def begin_callback():
        log.info('\n********** news begin **********')
        # 更新任务状态 doing

    def end_callback():
        log.info('\n********** news end **********')


    # 配置spider
    spider = Spider(tab_urls = 'mms_urls', begin_callback = begin_callback, end_callback = end_callback, delete_tab_urls = True, parser_params = program_info)

    # 添加parser
    # spider.add_parser(iqiyi_hot_parser)
    spider.add_parser(iqiyi_search_parser)
    # spider.add_parser(weibo_user_parser)
    # spider.add_parser(weibo_article_parser)

    spider.start()

if __name__ == '__main__':
    main()
