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

    def process_item(self, item, spider):
        try:
            test = item['show_id']
            if test == None:
                return item
        except:
            return item
        try:
            self.cursor.execute("""INSERT INTO episodes (show_id, format, season, episode, ed2k_link) VALUES (%s, %s, %s, %s, %s)""", (item['show_id'].encode('utf-8'), item['format'].encode('utf-8'), str(item['season']), str(item['episode']), item['ed2k_link'].encode('utf-8')))
            self.conn.commit()


        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])


        return item
