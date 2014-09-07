from celery import Celery
from crawler import EpisodesCrawler, ShowInfoCrawler, ShowPicCrawler

crawl_show_task = Celery('crawl_show', broker='amqp://guest@localhost//')
crawl_show_info_task = Celery('crawl_show_info', broker='amqp://guest@localhost//')
crawl_show_pic_task = Celery('crawl_show_pic', broker='amqp://guest@localhost//')

@crawl_show_task.task
def crawl_show(show_id):
    ec = EpisodesCrawler()
    ec.crawl(show_id)

@crawl_show_info_task.task
def crawl_show_info(show_name, show_id):
    sic = ShowInfoCrawler()
    sic.crawl(show_name, show_id)

@crawl_show_pic_task.task
def crawl_show_pic(subject_id, show_id):
    spc = ShowPicCrawler()
    spc.crawl(subject_id, show_id)

