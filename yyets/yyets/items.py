# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class YyetsItem(Item):
    # define the fields for your item here like:
    # name = Field()
    show_id = Field()
    format = Field()
    season = Field()
    episode = Field()
    ed2k_link = Field()
