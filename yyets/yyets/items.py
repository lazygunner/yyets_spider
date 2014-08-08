# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class YyetsItem(Item):
    # define the fields for your item here like:
    # name = Field()
    e_index = Field()
    show_id = Field()
    format = Field()
    season = Field()
    episode = Field()
    ed2k_link = Field()


class ShowItem(Item):

    show_id = Field()
    show_name = Field()
    created_time = Field()
    updated_time = Field()
    latest_season = Field()
    latest_episode = Field()

class ShowIDItem(Item):

    show_id = Field()
