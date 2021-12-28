from scrapy.crawler import CrawlerProcess
from OrcaScraper.spiders.orca import OrcaSpider
from OrcaScraper.pipelines import OrcascraperPipeline

class OrcaTransactionProcessor:
    def __init__(self, user, pw, start=None, end=None):
        self.user = user 
        self.pw = pw 
        self.start = start 
        self.end = end 

    def fetch(self, queue):
        items = []
        process = CrawlerProcess({
            'ROBOTSTXT_OBEY': True,
            'LOG_LEVEL': 'INFO',
            'BOT_NAME': 'OrcaScraper',
            'SPIDER_MODULES': ['OrcaScraper.spiders'],
            'NEWSPIDER_MODULE': 'OrcaScraper.spiders',
            'ITEM_PIPELINES': {
                'server_scrapy_bridge.ItemCollectorPipeline': 300,
            }
        })
        process.crawl(OrcaSpider, username=self.user, password=self.pw, startdate=self.start, enddate=self.end, items=items)
        process.start()
        queue.put(items)
        
class ItemCollectorPipeline(OrcascraperPipeline):
    def process_item(self, item, spider):
        processed = super().process_item(item, spider)
        spider.items.append(processed)