from celery import Celery
from crawler import EpisodesCrawler, ShowInfoCrawler, ShowPicCrawler
from xunlei import XunLeiClient

broker = 'amqp://guest@shooot.me//'
crawl_show_task = Celery('crawl_show', broker=broker)
crawl_show_info_task = Celery('crawl_show_info', broker=broker)
crawl_show_pic_task = Celery('crawl_show_pic', broker=broker)
remote_download_task = Celery('remote_download', borker=broker)


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


@remote_download_task.task
def remote_download_following(show_id, season, episode, url):
    xl = XunLeiClient()
    xl.remote_download_following(show_id, season, episode, url)
