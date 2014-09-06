import re
from scrapy.spider import Spider
from scrapy.selector import Selector

from douban.items import ShowInfoItem

class DoubanShowInfoSpider(Spider):
    name = "douban_show_info"
    start_urls = []

    def __init__(self, show_name, show_id):
        url = "http://www.douban.com/search?cat=1002&q=" + show_name
        self.show_id = show_id
        self.start_urls.append(url)

    def parse(self, response):
        show_info_item = ShowInfoItem()
        sel = Selector(response)
        for result in sel.xpath('//div[@class="result-list"]'):
            title = result.xpath('div[@class="result"]/div[@class="content"]/div[@class="title"]')[0]
            link_str = title.xpath('h3/a/@href').extract()[0]
            rate = title.xpath('div[@class="rating-info"]/span[@class="rating_nums"]/text()').extract()[0]

            p = re.compile(r'url=(.*?subject%2F(\d+)%2F.*?)&query')
            link = p.findall(link_str)
            if len(link) > 0:
                show_info_item['subject_id'] = link[0][1]
            show_info_item['douban_rate'] = float(rate)
            show_info_item['show_id'] = self.show_id
            yield show_info_item
            break