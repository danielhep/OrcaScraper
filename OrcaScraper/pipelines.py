# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.loader import ItemLoader
from OrcaScraper.items import RefactoredTransactionItem
import re
import logging

class OrcascraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Get Agency
        locationMatch = re.search(r'(...), (.*)', adapter.get('location'))
        agencyCode, location = locationMatch.group(1,2)
        routeMatch = re.search(r'Route (.+)', adapter.get('desc'))
        if routeMatch:
            route = routeMatch.group(1)
        else:
            route = None
        newItem = RefactoredTransactionItem(
            agency = agencyCode,
            sn = adapter.get('sn'),
            date = adapter.get('date'),
            desc = adapter.get('desc'),
            location = location,
            route = route,
            product = adapter.get('product'),
            amount = adapter.get('amount'),
            balance = adapter.get('balance'),
            paymentMethod = adapter.get('paymentMethod'),
        )
        return newItem
