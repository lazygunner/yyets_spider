import re
from scrapy.spider import Spider
from scrapy.selector import Selector

from douban.items import ShowPicItem

class DoubanShowPicSpider(Spider):
    name = "douban_show_pic"
    start_urls = []

    def __init__(self, subject_id, show_id):
        url = "http://movie.douban.com/subject/%s/photos?type=R" % subject_id
        self.show_id = show_id
        self.start_urls.append(url)

    def parse(self, response):
        show_pic_item = ShowPicItem()
        sel = Selector(response)
        for pic in sel.xpath('//ul/li/div[@class="cover"]/a/img'):

            pic_urls = pic.xpath('@src').extract()

            if len(pic_urls) > 0:
                pic_url = pic_urls[0]
                print 'pic:', pic_url
                show_pic_item['pic_url'] = pic_url
                show_pic_item['show_id'] = self.show_id
                yield show_pic_item
                break
