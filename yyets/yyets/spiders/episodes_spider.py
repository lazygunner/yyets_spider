# -*- coding: utf-8 -*-


from scrapy.spider import Spider
from scrapy.selector import Selector

from urllib2 import quote
import json
from yyets.items import YyetsItem
import re

class EpisodesSpider(Spider):
    name = "episodes"
    allowed_domains = ["yyets.com"]
    show_name = ""
    start_urls = [
    ]

    def __init__(self, show_id):
        self.show_id = quote(show_id.encode('utf-8'))
        self.start_urls.append("http://www.yyets.com/resource/" + self.show_id)

    def parse(self, response):
        #parse the episodes info
        #format='.*?'
        #p = re.compile(r'<li.*?itemid="(\d*)" format="(' + format + ')">.*?title=".*?\.[sS](\d{2})[eE](\d{2}).*?type="ed2k"\shref="(.*?)".*?</li>')
        #episodes = p.findall(html)
        sel = Selector(response)
        for ul in sel.xpath('//ul[@class="resod_list"]'):
            season = int(ul.xpath('@season').extract()[0])
            if season > 100:
                continue
            for li in ul.xpath('li[@itemid]'):
                item = YyetsItem()
                item['episode'] = int(li.xpath('@episode').extract()[0])
                item['show_id'] = unicode(self.show_id)
                item['format'] = li.xpath('@format').extract()[0]

                item['season'] = season
                item['ed2k_link'] = li.xpath('div/div/a[@type="ed2k"]/@href').extract()[0]
                item['e_index'] = '%d%02d%s' % (item['season'], item['episode'], item['format'])
                yield item







