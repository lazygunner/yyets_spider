# Scrapy settings for douban project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'douban'

SPIDER_MODULES = ['douban.spiders']
NEWSPIDER_MODULE = 'douban.spiders'

ITEM_PIPELINES = {'douban.pipelines.MySQLStorePipeLine':300}


DB_SETTINGS = {'user': 'gunner',
    'passwd': '17097448ak47',
    'db': 'yyets',
    'host': '115.28.223.15',
    'port': 30000}

CACHE_SETTINGS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'douban (+http://www.yourdomain.com)'
