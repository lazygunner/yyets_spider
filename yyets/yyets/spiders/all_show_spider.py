from scrapy.spider import Spider
from scrapy.selector import Selector

from urllib2 import quote
import json
from yyets.items import ShowItem
from yyets.settings import DOMAIN

class AllShowSpider(Spider):
    name = "all_show"
    start_urls = []

    def __init__(self):
        self.start_urls.append(DOMAIN + "/tv/schedule")

    def parse(self, response):
        sel = Selector(response)

        a_list = []
        a_list.extend(sel.xpath('//td[@class="ihbg "]/dl/dd/a'))
        a_list.extend(sel.xpath('//td[@class="ihbg cur"]/dl/dd/a'))
        for a in a_list:
            show_item = ShowItem()
            link = a.xpath('@href').extract()[0]
            link_list = link.split('/')
            if len(link_list) > 0:
                link_list.reverse()
                show_item['show_id'] = link_list[0]
            else:
                show_item['show_id'] = ''
            show_item['show_name'] = a.xpath('@title')[0].extract()
            yield show_item




























