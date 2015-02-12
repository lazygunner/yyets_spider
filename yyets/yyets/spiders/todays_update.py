# encoding:utf-8
import sys
import os
from datetime import datetime, timedelta
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path+'/..')

import json
import redis
from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule
from scrapy.selector import Selector

from items import ShowIDItem
from yyets.settings import CACHE_SETTINGS, YYETS_SETTINGS, DOMAIN

class UpdateTodaySpider(InitSpider):

    def __init__(self, yesterday=False):
        self.username = YYETS_SETTINGS['username']
        self.password = YYETS_SETTINGS['password']
        self.redis_conn = redis.Redis(host=CACHE_SETTINGS['host'], port=CACHE_SETTINGS['port'], db=CACHE_SETTINGS['db'])
        self.yesterday = yesterday

    name = 'update_today'
    login_page = DOMAIN + '/user/login/ajaxLogin'
    start_urls = [DOMAIN + '/today']

    rules = (
        Rule(SgmlLinkExtractor(),
             callback='parse_items', follow=True),
    )


    def init_request(self):
        print '================='
        """Generate a login request."""
        return FormRequest(url=self.login_page,
                    formdata={'account': self.username, 'password': self.password, 'remember':'0', 'from':'loginpage'},
                    callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        rsp = json.loads(response.body)
        if rsp['status'] == 1:
            self.log("Successfully logged in. Let's start crawling!")
            # Now the crawling can begin..
            return Request(url=self.start_urls[0], callback=self.parse_items)
        else:
            self.log("%s", rsp['info'])
            # Something went wrong, we couldn't log in, so nothing happens.


    def parse_items(self, response):
        show_id_item = ShowIDItem()
        sel = Selector(response)
        show_list = []
        latest_time = None
        last_updated_time = self.redis_conn.get('last_updated_time')
        if isinstance(last_updated_time, str) and last_updated_time != 'None':
            last_updated_time = datetime.strptime(last_updated_time, "%Y-%m-%d %H:%M:%S")
        else:
            last_updated_time = datetime(1900,1,1)
        today = datetime.now() - timedelta(days=1) if self.yesterday else datetime.now()
        today = datetime.strftime(today, "%02m-%02d")
        sel_string = '//tr[@channel="tv" and @day="%s"]' % today
        for tr in sel.xpath(sel_string):
            link = tr.xpath('td[not(@class="dr_ico")]/a/@href').extract()[0]
            time = tr.xpath('td[@class="d6"]/text()').extract()[0]
            time = datetime.strptime(time, '%H:%M')
            if not latest_time:
                latest_time = time
            link = link.split('/')
            if len(link) > 0:
                link.reverse()
                show_id = link[0]
                if show_id not in show_list:
                    if self.yesterday or time > last_updated_time:
                        show_list.append(show_id)
                        show_id_item['show_id'] = show_id
                        print show_id
                        print time
                        yield show_id_item
        print latest_time
        if not self.yesterday:
            self.redis_conn['last_updated_time'] = latest_time



