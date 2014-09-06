import re
from scrapy.spider import Spider
from scrapy.selector import Selector

from douban.items import ShowPicItem

class DoubanShowInfoSpider(Spider):
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

            import pdb;pdb.set_trace()
            pic_url = pic.xpath('@src').extract()[0]

            show_pic_item['pic_url'] = pic_url
            show_pic_item['show_id'] = self.show_id
            yield show_pic_item
            break
