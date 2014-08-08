#encoding:utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import pymysql
import hashlib
from datetime import datetime

from scrapy.http import Request
from spiders.episodes_spider import EpisodesSpider
from tasks import crawl_show

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
        self.conn = pymysql.connect(user='gunner', passwd='17097448ak47', db='yyets', host='rdszbq63qqmzeya.mysql.rds.aliyuncs.com',  charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.items = []

    def process_item(self, item, spider):
        #try:
        #    test = item['show_id']
        #    if test == None:
        #        return item
        #except:
        #    return item
        self.items.append(item)
        return item
    def open_spider(self, spider):
        pass

    def __get_new_episodes(self, show_id):
        rows = self.cursor.execute("""SELECT 'e_index', 'ed2k_link' FROM episodes WHERE show_id = %s""", show_id)
        old_episodes = self.cursor.fetchall()
        old_epi_dict = {}
        items = []
        l_e = 0
        l_s = 0
        for i in old_episodes:
            old_epi_dict[i[0]] = i[1]
        for item in self.items:
            e_index = item['e_index']

            if e_index not in old_epi_dict or item['ed2k_link'] == old_epi_dict[e_index]:
                item_tuple = (item['e_index'], item['show_id'], item['format'], item['season'], item['episode'], item['ed2k_link'])
                items.append(item_tuple)
                l_e = item['episode'] if item['episode'] > l_e else l_e
                l_s = item['season'] if item['season'] > l_s else l_s
        return (items, l_e, l_s)

    def _handle_episodes(self, show_id):
        new_items, l_e, l_s = self.__get_new_episodes(show_id)

        try:
            self.cursor.executemany("""REPLACE INTO episodes (e_index, show_id, format, season, episode, ed2k_link) VALUES (%s, %s, %s, %s, %s, %s)""", new_items)
            self.conn.commit()
            self.cursor.execute("""UPDATE shows SET updated_time=%s, latest_season=%s, latest_episode=%s WHERE show_id=%s""", (datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"), l_s, l_e, show_id))
            self.conn.commit()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])


    def _handle_all_show(self):
        shows = []
        date = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

        for show in self.items:
            show_tuple = (show['show_id'], show['show_name'], date, date, 0, 0)
            shows.append(show_tuple)

        try:
            self.cursor.executemany("""REPLACE INTO shows (show_id, show_name, created_time, updated_time, latest_season, latest_episode) \
                    VALUES (%s, %s, %s, %s, %s, %s)""", shows)
            self.conn.commit()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

    def close_spider(self, spider):

        if spider.name  == 'episodes':
            self._handle_episodes(spider.show_id)
        elif spider.name == 'all_show':
            self._handle_all_show()

        self.cursor.close()
        self.conn.close()


