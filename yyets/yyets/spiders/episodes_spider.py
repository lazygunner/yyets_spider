# -*- coding: utf-8 -*-


from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule

from urllib2 import quote
import json
from yyets.items import YyetsItem
import re

class EpisodesSpider(InitSpider):
    name = "episodes"
    allowed_domains = ["yyets.com"]
    show_name = ""
    start_urls = []
    login_page = 'http://www.yyets.com/user/login/ajaxLogin'

    def __init__(self, show_id):
        self.username = 'gunnerak'
        self.password = '880420'

        self.allowed_domains = ['yyets.com']

        self.show_id = quote(show_id.encode('utf-8'))
        self.start_urls = ["http://www.yyets.com/resource/" + self.show_id]

    rules = (
        Rule(SgmlLinkExtractor(),
        callback='parse_items', follow=True),
    )


    def init_request(self):
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
            print self.start_urls
            return Request(url=self.start_urls[0], callback=self.parse_items)
        else:
            self.log("%s", rsp['info'])
             # Something went wrong, we couldn't log in, so nothing happens.

    def parse_items(self, response):
        #parse the episodes info
        #format='.*?'
        #p = re.compile(r'<li.*?itemid="(\d*)" format="(' + format + ')">.*?title=".*?\.[sS](\d{2})[eE](\d{2}).*?type="ed2k"\shref="(.*?)".*?</li>')
        #episodes = p.findall(html)
        p = re.compile(r'\.[sS](\d*)[eE](\d*)\.')
        sel = Selector(response)
        for ul in sel.xpath('//ul[@class="resod_list"]'):
            season = ul.xpath('@season').extract()
            season = int(season[0]) if season else None
            if season > 100:
                continue
            for li in ul.xpath('li[@itemid]'):
                item = YyetsItem()
                episode = li.xpath('@episode').extract()
                item['episode'] = int(episode[0]) if episode else None
                item['show_id'] = unicode(self.show_id)
                fmt = li.xpath('@format').extract()
                item['format'] = fmt[0] if fmt else None

                item['season'] = season
                ed2k = li.xpath('div/div/a[@type="ed2k"]/@href').extract()
                item['ed2k_link'] = ed2k[0] if ed2k else None
                #Correct episode if it's larger than 100
                if item['ed2k_link']:
                    ep = p.findall(item['ed2k_link'])
                    if ep and len(ep[0]) == 2:
                        item['season'] = int(ep[0][0])
                        item['episode'] = int(ep[0][1])
                item['e_index'] = '%s:%d:%d:%s' % (item['show_id'], item['season'], item['episode'], item['format'])
                yield item







