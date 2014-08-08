from celery import Celery
from crawler import EpisodesCrawler

crawl_show_task = Celery('crawl_show', broker='amqp://guest@localhost//')

@crawl_show_task.task
def crawl_show(show_id):
    ec = EpisodesCrawler()
    ec.crawl(show_id)

