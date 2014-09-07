# Scrapy settings for yyets project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'yyets'

SPIDER_MODULES = ['yyets.spiders']
NEWSPIDER_MODULE = 'yyets.spiders'

ITEM_PIPELINES = {'yyets.pipelines.AddToCeleryPipeLine':200, 'yyets.pipelines.MySQLStorePipeLine':300}
USER_AGENT = 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
LOG_FILE = 'scrapy.log'


DB_SETTINGS = {'user': 'gunner',
    'passwd': '17097448ak47',
    'db': 'yyets',
    'host': '0.0.0.0',
    'port': 30000}

CACHE_SETTINGS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

YYETS_SETTINGS = {
    'username': 'gunnerak',
    'password': '880420'
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'yyets (+http://www.yourdomain.com)'
