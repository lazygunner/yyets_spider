from scrapy.spider import Spider
from urllib2 import quote
import json

from tasks import crawl_show

class ShowSpider(Spider):
    name = "show"
    allowed_domains = ["yyets.com"]
    show_name = ""
    start_urls = [
    ]

    def __init__(self, show_name):
        self.show_name = quote(show_name.encode('utf-8'))
        self.start_urls.append("http://www.yyets.com/search/api?keyword=" + self.show_name)

    def parse(self, response):
        result_json = json.loads(response.body)
        results = result_json["data"]

        if results == False:
            print 'Show name error, cannot find it in YYets'
            return 'no'
        shows = []
        show = {}
        for res in results:
            if(res['type'] == 'resource' and res['channel'] == 'tv'):
                show = res
                shows.append(show)
        if len(shows) == 0:
            print 'Cannot find TV show according to the name!'
            return 'no'
        #else:
            #if _debug:
               # print 'find the resource ' + show['itemid'] + ' ' + show['title']
        #save show info
        for show in shows:
            show_id = show['itemid']
            print show
            crawl_show.delay(show_id)
        #show_item = Show.objects(show_id=show_id).first()
        #if show_item == None:
        #    t = threading.Thread(target=add_new_show_thread, args=[show], name="add_new_show_thread")
        #    t.start()
        #    return 'ad'
        #else:
        #    if _debug:
        #        print show_item.latest_episode
