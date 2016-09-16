from celery import Celery
from crawler import EpisodesCrawler
from xunlei import XunLeiClient

broker = 'amqp://guest@folo.xyz//'
crawl_show_task = Celery('crawl_show', broker=broker)
crawl_show_info_task = Celery('crawl_show_info', broker=broker)
crawl_show_pic_task = Celery('crawl_show_pic', broker=broker)
remote_download_task = Celery('remote_download', borker=broker)


@crawl_show_task.task
def crawl_show(show_id):
    ec = EpisodesCrawler()
    ec.crawl(show_id)


@remote_download_task.task
def remote_download_following(show_id, season, episode, url):
    xl = XunLeiClient()
    xl.remote_download_following(show_id, season, episode, url)
