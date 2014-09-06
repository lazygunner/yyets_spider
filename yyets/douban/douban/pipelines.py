# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from datetime import datetime
from .settings import DB_SETTINGS


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
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def _handle_show_info(self):

        #logging.info('%s %s %s %s', show_id, l_e, l_s, len(new_items))
        douban_show_info = self.items[0]
        try:

            query_str = """UPDATE shows SET updated_time=%s, subject_id=%s, douban_rate=%s"""
            query_str += ' WHERE show_id=%s'
            self.cursor.execute(query_str,
                                (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
                                douban_show_info['subject_id'],
                                douban_show_info['douban_rate'],
                                douban_show_info['show_id']))
            self.conn.commit()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def _handle_show_pic(self):

        #logging.info('%s %s %s %s', show_id, l_e, l_s, len(new_items))
        douban_show_pic = self.items[0]
        import pdb;pdb.set_trace()
        try:

            query_str = """UPDATE shows SET pic_url=%s"""
            query_str += ' WHERE show_id=%s'
            self.cursor.execute(query_str,
                                (douban_show_pic['pic_url'],
                                douban_show_pic['show_id']))
            self.conn.commit()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def close_spider(self, spider):
        if spider.name == 'douban_show_info':
            self._handle_show_info()
        if spider.name == 'douban_show_pic':
            self._handle_show_pic()


        self.cursor.close()
        self.conn.close()