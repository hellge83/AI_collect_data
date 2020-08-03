# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy
        
        
    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        
        src = spider.name
        salary = item['item_salary']
        url = item['item_url']
        
        if spider.name == 'hhru':
            item['_id'], item['link'] = self.process_hh_url(url, src)
            item['min_salary'], item['max_salary'], item['currency'] = self.process_hh_salary(salary)       
        elif spider.name == 'sjru':
            item['_id'], item['link'] = self.process_sj_url(url, src)
            item['min_salary'], item['max_salary'], item['currency'] = self.process_sj_salary(salary)        
        else:
            pass
        
        del item['item_salary']
        del item['item_url']

        collection.update_one({'_id': item['_id']}, {'$set': item}, upsert = True)
        return item
    
    
    def process_hh_salary(self, salary):
        if len(salary) == 1:
            min_salary, max_salary, currency = None, None, None
        elif len(salary) == 7:
            min_salary = int(salary[1].replace('\xa0', ''))
            max_salary = int(salary[3].replace('\xa0', ''))
            currency = salary[5]
        elif len(salary) == 5:
            if salary[0] == 'от ':
                min_salary = int(salary[1].replace('\xa0', ''))
                max_salary = None
                currency = salary[3]
            elif salary[0] == 'до ':
                min_salary = None
                max_salary = int(salary[1].replace('\xa0', ''))
                currency = salary[3]
            else: # если пропустила еще какой-то вариант - отловить
                min_salary, max_salary, currency = 'missed_from_to', 'missed_from_to', 'missed_from_to'
        else: # если пропустила еще какой-то вариант - тут тоже отловить
            min_salary, max_salary, currency = 'missed_len', 'missed_len', 'missed_len'
        return min_salary, max_salary, currency
    
    def process_hh_url(self, url, src):
        _id = src + '_' + url[url.rindex('https://kaliningrad.hh.ru/vacancy/') + 34 : url.rindex('?')]
        url = url[: url.rindex('?')]
        return _id, url
    
    def process_sj_salary(self, salary):
        if len(salary) == 1:
            min_salary, max_salary, currency = None, None, None
        elif len(salary) == 4:
            min_salary = int(salary[0].replace('\xa0', ''))
            max_salary = int(salary[1].replace('\xa0', ''))
            currency = salary[3]
            
        elif len(salary) == 3:
            if salary[0] == 'от':
                min_salary = int(salary[2][: salary[2].rindex('\xa0')].replace('\xa0', ''))
                max_salary = None
                currency = salary[2][salary[2].rindex('\xa0') + 1:]
            elif salary[0] == 'до':
                min_salary = None
                max_salary = int(salary[2][: salary[2].rindex('\xa0')].replace('\xa0', ''))
                currency = salary[2][salary[2].rindex('\xa0') + 1:]
            else: 
                min_salary = int(salary[0])
                max_salary = int(salary[0])
                currency = salary[2]
        else: # если пропустила еще какой-то вариант - тут тоже отловить
            min_salary, max_salary, currency = 'missed_len', 'missed_len', 'missed_len'
        return min_salary, max_salary, currency
    
    def process_sj_url(self, url, src):
        _id = src + '_' + url[url.rindex('-') + 1 : url.rindex('.')]
        url = url
        return _id, url
        
