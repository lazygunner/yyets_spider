# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ShowInfoItem(Item):

    show_id = Field()
    subject_id = Field()
    douban_rate = Field()


class ShowPicItem(Item):

    show_id = Field()
    pic_url = Field()