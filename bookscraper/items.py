# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_price(num):
    try:
        num = int(num)
    except:
        pass
    return num

class BookscraperItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field
    name = scrapy.Field()
    link = scrapy.Field()
    authors = scrapy.Field()
    price = scrapy.Field()
    discount_price = scrapy.Field()
    rating = scrapy.Field()

class LeroyscraperItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    pictures = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())

