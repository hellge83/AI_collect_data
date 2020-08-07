# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy


class LeroymerlinPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlin
        
        
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        # добавляем в бд
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert = True)
        return item
    
class  LeroymerlinPhotoPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)
