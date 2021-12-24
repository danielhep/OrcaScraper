# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field, Item
from itemloaders.processors import Compose, TakeFirst


strip_str = Compose(TakeFirst(), str.strip)
convert_int = Compose(strip_str, lambda x: int(x) if x != "-" else None)
convert_float = Compose(strip_str, lambda x: float(x) if x != "-" else None)

class TransactionItem(Item):
    sn = Field(output_processor=convert_int)
    date = Field(output_processor=strip_str)
    desc = Field(output_processor=strip_str)
    location = Field(output_processor=strip_str)
    product = Field(output_processor=strip_str)
    amount = Field(output_processor=convert_float)
    balance = Field(output_processor=convert_float)
    paymentMethod = Field(output_processor=strip_str)