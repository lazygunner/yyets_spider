# encoding:utf-8
import sys
import os
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
from datetime import datetime, timedelta

class UpdateTodaySpider(InitSpider):

    def __init__(self):
        self.username = 'gunnerak'
        self.password = '880420'
        self.redis_conn = redis.Redis(host='127.0.0.1', port=6379, db=0)

    name = 'update_today'
    allowed_domains = ['yyets.com']
    login_page = 'http://www.yyets.com/user/login/ajaxLogin'
    start_urls = ['http://www.yyets.com/today']

    rules = (
        Rule(SgmlLinkExtractor(),
             callback='parse_items', follow=True),
    )


    def init_request(self):
        print '================='
        """Generate a login request."""
        return FormRequest(url=self.login_page,
                    formdata={'account': self.username, 'password': self.password, 'type': 'nickname', 'remember':'0'},
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
        today = datetime.now()
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
                if show_id not in show_list and time > last_updated_time:
                    show_list.append(show_id)
                    show_id_item['show_id'] = show_id
                    print show_id
                    print time
                    yield show_id_item
        print latest_time
        self.redis_conn['last_updated_time'] = latest_time



