# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class InstagramPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram
    
    
    def process_item(self, item, spider):
        collection = self.mongo_base[item['user_id']]
        item['_id'] = item['utype'] + '_' + item['uid']
        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert = True)
        return item
