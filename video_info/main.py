import sys
sys.path.append('../')
import init
import pid
pid.record_pid(__file__)
import utils.tools as tools
from utils.log import log
from base.spider import Spider
from utils.export_data import ExportData

# 需配置
from video_info.parsers import *

def main():
    def begin_callback():
        log.info('\n********** news begin **********')
        # 更新任务状态 doing

    def end_callback():
        log.info('\n********** news end **********')



    # 配置spider
    spider = Spider(tab_urls = 'mms_urls', begin_callback = begin_callback, end_callback = end_callback, delete_tab_urls = True)

    # 添加parser
    spider.add_parser(iqiyi_parser)

    spider.start()

if __name__ == '__main__':
    main()