import logging

import pymysql
from xunleipy.vod import XunLeiVod
from xunleipy.remote import XunLeiRemote

from yyets.settings import DB_SETTINGS, XUNLEI_SETTINGS as xl

logger = logging.getLogger(__name__)


class XunLeiClient(object):
    def __init__(self):
        self.conn = None
        self.cursor = None
        try:
            self.conn = pymysql.connect(
                user=DB_SETTINGS['user'],
                passwd=DB_SETTINGS['passwd'],
                db=DB_SETTINGS['db'],
                host=DB_SETTINGS['host'],
                port=DB_SETTINGS['port'],
                charset="utf8",
                use_unicode=True
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.exception(str(e))

    def remote_download_following(self, show_id, s, e, url):
        try:
            sql = """SELECT * FROM follows
                WHERE show_id = %s AND
                latest_season <= %s AND
                latest_episode <= %s
            """
            self.cursor.execute(sql, show_id, s, e)
            followers = self.cursor.fetchall()
        except pymysql.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])

        if not followers:
            return

        link = url.split('|')
        name = link[2]
        file_size = link[3]
        remote_data = {
            'url': url,
            'name': name,
            'gcid': '',
            'cid': '',
            'file_size': file_size
        }

        for follower in followers:
            # TODO add user xunlei client
            xlr = XunLeiRemote(
                xl['username'], xl['password'])
            rtn = xlr.add_tasks_to_remote(
                0,
                'C:/TDDOWNLOAD/TV',
                [remote_data]
            )
            if rtn['rtn'] != 0:
                print rtn
