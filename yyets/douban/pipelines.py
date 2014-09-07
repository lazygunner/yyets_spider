# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import logging
from datetime import datetime
from tasks import crawl_show_pic
from .settings import DB_SETTINGS

logging.basicConfig(filename='pipeline.log',level=logging.DEBUG)

class MySQLStorePipeLine(object):
    def __init__(self):
        self.conn = pymysql.connect(user=DB_SETTINGS['user'],
                                    passwd=DB_SETTINGS['passwd'],
                                    db=DB_SETTINGS['db'],
                                    host=DB_SETTINGS['host'],
                                    port=DB_SETTINGS['port'],
                                    charset="utf8",
                                    use_unicode=True)

        self.cursor = self.conn.cursor()
        #self.redis_conn = redis.Redis(CACHE_SETTINGS['host'], CACHE_SETTINGS['port'], CACHE_SETTINGS['db'])
        self.info_items = []
        self.pic_items = []

    def process_item(self, item, spider):
        print 'info_spider:', spider.name
        if spider.name == 'douban_show_info':
            self.info_items.append(item)
        elif spider.name == 'douban_show_pic':
            self.pic_items.append(item)
        return item

    def _handle_show_info(self):

        #logging.info('%s %s %s %s', show_id, l_e, l_s, len(new_items))
        if len(self.info_items) == 0:
            return
        print 'items:', self.info_items
        douban_show_info = self.info_items[0]
        print 'save show_info:', douban_show_info
        logging.debug('save show_info:%s', douban_show_info)
        try:
            query_str = """UPDATE shows SET updated_time=%s, subject_id=%s, douban_rate=%s"""
            query_str += ' WHERE show_id=%s'
            self.cursor.execute(query_str,
                                (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                                douban_show_info['subject_id'],
                                douban_show_info['douban_rate'],
                                douban_show_info['show_id']))
            self.conn.commit()
            crawl_show_pic.delay(douban_show_info['subject_id'], douban_show_info['show_id'])
            self.items = []
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def _handle_show_pic(self):

        #logging.info('%s %s %s %s', show_id, l_e, l_s, len(new_items))
        if len(self.pic_items) == 0:
            return
        douban_show_pic = self.pic_items[0]
        try:
            print 'save show_pic:', douban_show_pic
            logging.debug('save show_pic:%s', douban_show_pic)
            query_str = """UPDATE shows SET pic_url=%s"""
            query_str += ' WHERE show_id=%s'
            self.cursor.execute(query_str,
                                (douban_show_pic['pic_url'],
                                douban_show_pic['show_id']))
            self.conn.commit()
            self.items = []
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def close_spider(self, spider):
        if spider.name == 'douban_show_info':
            self._handle_show_info()
        elif spider.name == 'douban_show_pic':
            self._handle_show_pic()


        self.cursor.close()
        self.conn.close()
