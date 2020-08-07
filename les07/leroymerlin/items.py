# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import Compose, MapCompose, TakeFirst
from w3lib.html import remove_tags
import re

def process_photos(value):
    if value[:2] == '//':
        return f'http:{value}'
    return value

def process_digits(values):
    return [float(val) if val.replace('.', '', 1).isdigit() else val for val in values]
        

def process_info(params):
    params = [re.sub(r'\s+', ' ', ':'.join(i.split('\n '))).strip(': ').replace(':', '') for i in params]
    result = {}
    for i in params:
        d = i.split('  ')
        result[d[0]] = d[1]
    return result
    

class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photos))
    url = scrapy.Field()
    _id = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=Compose(process_digits), output_processor=TakeFirst()) # в число сделать!
    info = scrapy.Field(input_processor=MapCompose(remove_tags), output_processor=Compose(process_info))

