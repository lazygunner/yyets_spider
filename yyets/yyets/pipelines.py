#encoding:utf-8
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sys
import pymysql
import hashlib

from scrapy.http import Request

class YyetsPipeline(object):
    def process_item(self, item, spider):
        return item

class MySQLStorePipeLine(object):
    def __init__(self):
        self.conn = pymysql.connect(user='gunner', passwd='17097448ak47', db='yyets', host='rdszbq63qqmzeya.mysql.rds.aliyuncs.com',  charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()
        self.items = []

    def process_item(self, item, spider):
        try:
            test = item['show_id']
            if test == None:
                return item
        except:
            return item
        self.items.append(item)
    def open_spider(self, spider):
        #self.episode_count = self.cursor.execute("""SELECT COUNT(*) FROM episodes WHERE show_id = %s""", spider.show_id)
        #print 'hehe'
        #print self.episode_count
        pass

    def _get_new_episodes(self, show_id):
        rows = self.cursor.execute("""SELECT 'index', 'ed2k_link' FROM episodes WHERE show_id = %s""", show_id)
        old_episodes = self.cursor.fetchall()
        old_epi_dict = {}
        items = []
        #import pdb
        #pdb.set_trace()
        for i in old_episodes:
            old_epi_dict[i[0]] = i[1]
        for item in self.items:
            #item['format'] = item['format'].encode('utf-8')
            #item['show_id'] = item['show_id'].encode('utf-8')
            #item['index'] = item['index'].encode('utf-8')
            #item['ed2k_link'] = item['ed2k_link'].encode('utf-8')
            #item['season'] = str(item['season'])
            #item['episode'] = str(item['episode'])
            e_index = item['e_index']

            if e_index not in old_epi_dict or item['ed2k_link'] == old_epi_dict[e_index]:
                item_tuple = (item['e_index'], item['show_id'], item['format'], item['season'], item['episode'], item['ed2k_link'])
                items.append(item_tuple)
        return items


    def close_spider(self, spider):

        new_items = self._get_new_episodes(spider.show_id)

        try:
            #self.cursor.executemany("""INSERT INTO episodes (show_id, format, season, episode, ed2k_link) VALUES (%s, %s, %s, %s, %s)""", (item['show_id'].encode('utf-8'), item['format'].encode('utf-8'), str(item['season']), str(item['episode']), item['ed2k_link'].encode('utf-8')))
            print new_items[0]
            self.cursor.executemany("""REPLACE INTO episodes (e_index, show_id, format, season, episode, ed2k_link) VALUES (%s, %s, %s, %s, %s, %s)""", new_items)
            self.conn.commit()


        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

#        return item
