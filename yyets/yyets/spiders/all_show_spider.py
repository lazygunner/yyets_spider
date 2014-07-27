from scrapy.spider import Spider
from scrapy.selector import Selector

from urllib2 import quote
import json
from yyets.items import ShowItem

class AllShowSpider(Spider):
    name = "all_show"
    start_urls = []

    def __init__(self):
        self.start_urls.append("http://www.yyets.com/tv/schedule")

    def parse(self, response):
        sel = Selector(response)

        for a in sel.xpath('//td[@class="ihbg"]/dl/dd/a'):
            show_item = ShowItem()
            link = a.xpath('@href').extract()[0]
            link_list = link.split('/')
            if len(link_list) > 0:
                link_list.reverse()
                show_item['show_id'] = link_list[0]
            else:
                show_item['show_id'] = ''
            show_item['show_name'] = a.xpath('font//text()')[0].extract()
            print show_item['show_id']
            print show_item['show_name']
            yield show_item




























