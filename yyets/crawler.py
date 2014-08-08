
from scrapy.crawler import Crawler
from scrapy.conf import settings
from yyets.spiders.episodes_spider import EpisodesSpider
from scrapy import log, project, signals
from twisted.internet import reactor
from billiard import Process
from scrapy.utils.project import get_project_settings

class UrlCrawlerScript(Process):
    def __init__(self, spider):
        Process.__init__(self)
        settings = get_project_settings()
        self.crawler = Crawler(settings)

        if not hasattr(project, 'crawler'):
            self.crawler.install()
            self.crawler.configure()

        self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
        self.spider = spider

    def run(self):
        self.crawler.crawl(self.spider)
        self.crawler.start()
        reactor.run()

class EpisodesCrawler(object):

    def crawl(self, show_id):
        spider = EpisodesSpider(show_id)
        crawler = UrlCrawlerScript(spider)
        crawler.start()
        crawler.join()


if __name__ == "__main__":
    c = EpisodesCrawler()
    c.crawl('32142')

