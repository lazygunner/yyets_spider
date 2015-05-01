#encoding:utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import json
from datetime import datetime

import pymysql
import redis
from xunleipy.vod import XunLeiVod

from scrapy.http import Request
from spiders.episodes_spider import EpisodesSpider
from tasks import crawl_show
from .settings import DB_SETTINGS, CACHE_SETTINGS, XUNLEI_SETTINGS

logging.basicConfig(filename='pipeline.log',level=logging.DEBUG)

xunlei_vod = XunLeiVod(XUNLEI_SETTINGS['username'], XUNLEI_SETTINGS['password'])
print 'xunlei_session:', xunlei_vod.session.cookies.get('sessionid')

class YyetsPipeline(object):

    def process_item(self, item, spider):
        return item


class AddToCeleryPipeLine(object):
    def process_item(self, item, spider):
        if spider.name == 'update_today':
            crawl_show.delay(item['show_id'])
        return item


class MySQLStorePipeLine(object):
    def __init__(self):
        self.conn = None
        self.cursor = None
        try:
            self.conn = pymysql.connect(user=DB_SETTINGS['user'],
                                    passwd=DB_SETTINGS['passwd'],
                                    db=DB_SETTINGS['db'],
                                    host=DB_SETTINGS['host'],
                                    port=DB_SETTINGS['port'],
                                    charset="utf8",
                                    use_unicode=True)
            self.cursor = self.conn.cursor()

        except:
            return

        self.redis_conn = redis.Redis(CACHE_SETTINGS['host'], CACHE_SETTINGS['port'], CACHE_SETTINGS['db'])
        self.items = []

    def process_item(self, item, spider):
        #try:
        #    test = item['show_id']
        #    if test == None:
        #        return item
        #except:
        #    return item
        if spider.name in ['episodes', 'all_show']:
            self.items.append(item)
        return item

    def open_spider(self, spider):
        pass

    def __get_new_episodes(self, show_id):
        try:
            rows = self.cursor.execute("""SELECT e_index, ed2k_link FROM episodes WHERE show_id = %s""", show_id)
            old_episodes = self.cursor.fetchall()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        old_epi_dict = {}
        items = []
        l_e = 0
        l_s = 0
        l_s_e = 0

        for i in old_episodes:
            old_epi_dict[i[0]] = i[1]
        for item in self.items:
            e_index = item['e_index']

            if e_index not in old_epi_dict or item['ed2k_link'] != old_epi_dict[e_index]:
                item_tuple = (item['e_index'], item['show_id'], item['format'], item['season'], item['episode'], item['ed2k_link'], item['ed2k_link'])
                items.append(item_tuple)

            if item['season'] * 1000 + item['episode'] > l_s_e:
                l_s = item['season']
                l_e = item['episode']
                l_s_e = l_s * 1000 + l_e
        return (items, l_e, l_s)

    def _handle_episodes(self, show_id):
        new_items, l_e, l_s = self.__get_new_episodes(show_id)
        try:
            if len(new_items) > 0:
                logging.info('%s %s %s %s', show_id, l_e, l_s, len(new_items))

                self.cursor.executemany("""INSERT INTO episodes (e_index, show_id, format, season, episode, ed2k_link) VALUES (%s, %s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE ed2k_link=%s""", new_items)
                self.conn.commit()

                #vod_urls = [item[5] for item in new_items]
                #print xunlei_vod.add_task_to_vod(vod_urls)

            cache_name = '%s|%s' % ('show_info', show_id)
            show_info_str = self.redis_conn.get(cache_name)

            print 'update show:%s' % show_id, show_info_str
            update_str = ''
            key_str = 'show_id, created_time, updated_time'
            val_str = '%s,%s,%s'
            show_info = {}
            if show_info_str and show_info_str != 'None':
                show_info = json.loads(show_info_str)
                info_str = ''
                for key, value in show_info.items():
                    value_str = ''
                    if isinstance(value, list):
                        for v in value:
                            value_str += '%s ' % v
                    else:
                        value_str = value.replace('"', '""')
                    info_str += ',%s="%s"' % (key, value_str)
                    key_str += ',%s' % key
                    val_str += ',"%s"' %value_str
                update_str += info_str

            if l_e or l_s:
                update_str = u', latest_season={0}, latest_episode={1}{2}'.format(l_s, l_e, update_str)

            query_str = """INSERT INTO shows (""" + key_str +\
                    """) VALUES (""" + val_str +\
                    """) ON DUPLICATE KEY UPDATE updated_time=%s""" + update_str

            print 'query str:%s' % query_str
            now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
            self.cursor.execute(
                query_str,
                (show_id,
                now,
                now,
                now,
            ))
            self.conn.commit()

            for cate in show_info.get('show_type', []):
                if cate != '':
                    try:
                        category_query_str = """INSERT INTO shows_category (show_id, category_name) VALUES (%s, %s)"""
                        self.cursor.execute(category_query_str, (show_id, cate))
                        self.conn.commit()
                    except pymysql.Error as e:
                        continue

        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
        except Exception as e:
            print e

    def _handle_all_show(self):
        shows = []
        date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

        for show in self.items:
            show_tuple = (show['show_id'], show['show_name'], date, date, 0, 0, date)
            shows.append(show_tuple)
            #print 'add show_info task to celery:', show['show_name'], show['show_id']
            #crawl_show_info.delay(show['show_name'], show['show_id'])
            print 'new show:', show_tuple
        try:
            self.cursor.executemany("""INSERT INTO shows (show_id, show_name, created_time, updated_time, latest_season, latest_episode) \
                    VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE updated_time=%s""", shows)
            self.conn.commit()

        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def close_spider(self, spider):
        if spider.name == 'episodes':
            self._handle_episodes(spider.show_id)
        elif spider.name == 'all_show':
            self._handle_all_show()

        if self.cursor:
            self.cursor.close()
            self.conn.close()


