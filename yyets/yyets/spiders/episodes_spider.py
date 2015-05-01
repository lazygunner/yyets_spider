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
import redis
from yyets.settings import CACHE_SETTINGS, YYETS_SETTINGS, DOMAIN

class EpisodesSpider(InitSpider):
    name = "episodes"
    #allowed_domains = ["yyets.com"]
    show_name = ""
    start_urls = []
    login_page = DOMAIN + '/user/login/ajaxLogin'

    def __init__(self, show_id):
        self.username = YYETS_SETTINGS['username']
        self.password = YYETS_SETTINGS['password']
        self.redis_conn = redis.Redis(CACHE_SETTINGS['host'], CACHE_SETTINGS['port'], CACHE_SETTINGS['db'])

        self.show_id = quote(show_id.encode('utf-8'))
        self.start_urls = [DOMAIN + "/resource/list/" + self.show_id]

    rules = (
        Rule(SgmlLinkExtractor(),
        callback='parse_items', follow=True),
    )


    def init_request(self):
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

        cache_name = "%s|%s" % ('show_info', self.show_id)
        show_info = self.redis_conn.get(cache_name)
        if not show_info or show_info == 'None':

            show_info = {}
            tmp_show_name = sel.xpath('//h2[@class="tv"]/strong/text()').extract()
            if len(tmp_show_name) > 0:
                snp = re.compile(u'\u300a(.*?)\u300b', re.UNICODE)
                tmp_name = snp.findall(tmp_show_name[0])
                if len(tmp_name) > 0:
                    show_info['show_name'] = tmp_name[0]
                else:
                    show_info['show_name'] = tmp_show_name[0]
            for li in sel.xpath('//ul[@class="r_d_info"]/li'):
                spans = li.xpath('span/text()').extract()
                if len(spans) > 0:
                    span = spans[0]
                else:
                    continue
                if span == u'英文：':
                    strongs = li.xpath('strong/text()').extract()
                    strong = strongs[0] if strongs else ''
                    show_info['english_name'] = strong
                elif span == u'别名：':
                    show_info['other_name'] = li.xpath('text()').extract()[0].strip(' ')
                elif span == u'编剧：':
                    writers = []
                    hrefs = li.xpath('a')
                    for href in hrefs:
                        h = href.xpath('@href').extract()[0]
                        name = href.xpath('text()').extract()[0]
                        writers.append(name)
                    show_info['writers'] = writers
                elif span == u'主演：':
                    actors = []
                    hrefs = li.xpath('a')
                    for href in hrefs:
                        h = href.xpath('@href').extract()[0]
                        name = href.xpath('text()').extract()[0]
                        actors.append(name)
                    show_info['actors'] = actors
                elif span == u'导演：':
                    directors = []
                    hrefs = li.xpath('a')
                    for href in hrefs:
                        h = href.xpath('@href').extract()[0]
                        name = href.xpath('text()').extract()[0]
                        directors.append(name)
                    show_info['directors'] = directors
                elif span == u'播出：':
                    show_info['show_type'] = li.xpath('text()').extract()[1].split('/')
                elif span == u'简介：':
                    show_info['show_desc'] = li.xpath('p/text()').extract()[0]


            self.redis_conn[cache_name] = json.dumps(show_info)


        for ul in sel.xpath('//div[@class="media-list"]/ul'):
            for li in ul.xpath('li[@class="clearfix"]'):
                item = YyetsItem()
                season = li.xpath('@season').extract()
                episode = li.xpath('@episode').extract()
                season = int(season[0]) if season else None
                if season > 100:
                    continue
                item['season'] = season
                item['episode'] = int(episode[0]) if episode else None
                item['show_id'] = unicode(self.show_id)
                fmt = li.xpath('@format').extract()
                item['format'] = fmt[0] if fmt else None

                ed2k = li.xpath('div[@class="fr"]/a[@type="ed2k"]/@href').extract()
                item['ed2k_link'] = ed2k[0] if ed2k else None
                #Correct episode if it's larger than 100
                if item['ed2k_link']:
                    ep = p.findall(item['ed2k_link'])
                    if ep and len(ep[0]) == 2:
                        item['season'] = int(ep[0][0])
                        item['episode'] = int(ep[0][1])
                item['e_index'] = '%s:%d:%d:%s' % (item['show_id'], item['season'], item['episode'], item['format'])
                yield item






