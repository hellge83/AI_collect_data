# -*- coding: utf-8 -*-
"""
1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.ru/news
Для парсинга использовать xpath. Структура данных должна содержать:
* название источника,
* наименование новости,
* ссылку на новость,
* дата публикации
2)Сложить все новости в БД
"""
from lxml import html
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient


def get_response(url):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    response = requests.get(url, headers = headers)
    if response.ok:
        dom = html.fromstring(response.text)
    return dom


def lenta_news():
    lenta_url = 'https://lenta.ru'
    lenta_dom = get_response(lenta_url)
    lenta_blocks = lenta_dom.xpath("//section[contains(@class,'b-top7-for-main')]/*/div[contains(@class, 'item')]//a[@href]/time/..")
    
    lenta_news = []
    for block in lenta_blocks:
        news = {}
        news['name'] = block.xpath("./text()")[0].replace('\xa0', ' ')
        news['date'] = str(block.xpath("./time/@datetime")[0])
        
        news_time = news['date'][1:6]
        news_date = news['date'][8:]
        for old, new in [(' января ', '-01-'), (' февраля ', '-02-'), (' марта ', '-03-'), (' апреля ', '-04-'), (' мая ', '-05-'), (' июня ', '-06-'), (' июля ', '-07-'), (' августа ', '-08-'), (' сентября ', '-09-'), (' октября ', '-10-'), (' ноября ', '-11-'), (' декабря ', '-12-')]:
                news_date = news_date.replace(old, new)
        news['date'] = datetime.strptime(news_date + ' ' + news_time, '%d-%m-%Y %H:%M')
                
        news['url'] = block.xpath("./@href")
        if str(news['url'][0])[0] == '/':
            news['url'] = lenta_url + str(news['url'][0])
        # news['src'] = str(news['url'])[: str(news['url']).find('/news/')]
        news['src'] = news['url']
        lenta_news.append(news)
    return lenta_news


def get_mail_urls():
    mail_url = 'https://news.mail.ru'
    mail_dom = get_response(mail_url)
    mail_urls = mail_dom.xpath("//a[contains(@class, 'list__text')]/@href | //div[contains(@class, 'daynews_')]/a/@href")
    mail_urls = [mail_url + link if link[0] == '/' else str(link) for link in mail_urls]
    return mail_urls

def mail_news():
    mail_news = []
    mail_urls = get_mail_urls()
    
    for mail_url in mail_urls:
        mail_news_dom = get_response(mail_url)
        mail_news_block = mail_news_dom.xpath("//div[contains(@class, 'breadcrumbs')]/..")[0]
        
        news = {}
        news['name'] = str(mail_news_block.xpath(".//h1/text()")[0])
        news['date'] = mail_news_block.xpath(".//span[@class='breadcrumbs__item'][1]//span[@datetime]/@datetime")[0].replace('T', ' ')
        news['date'] = datetime.strptime(news['date'][:-6], '%Y-%m-%d %H:%M:%S')
        news['url'] = mail_url
        news['src'] = str(mail_news_block.xpath(".//span[@class='breadcrumbs__item'][2]//a[@target]/@href")[0])
        mail_news.append(news)
    return mail_news

def yandex_news():
    yandex_main_url = 'https://yandex.ru'
    yandex_url = 'https://yandex.ru/news/rubric/computers'
    yandex_dom = get_response(yandex_url)
    yandex_blocks = yandex_dom.xpath("//div[contains(@class, 'warn__owner')]/div[contains(@class, 'story')]")
    
    yandex_news = []
    for block in yandex_blocks:
        news = {}
        news['name'] = str(block.xpath(".//h2[@class='story__title']/a/text()")[0])
        news['info'] = str(block.xpath(".//div[@class='story__date']/text()")[0])
    
        news_datetime = news['info'][: -5].split(' ')[-1]
        news_time = news['info'][-5 :]
        if not news_datetime:
            news_date = datetime.now().strftime('%Y-%m-%d')
            news['date'] = datetime.strptime(news_date + ' ' + news_time, '%Y-%m-%d %H:%M')
        elif news_datetime == 'вчера\xa0в\xa0':
            news_date = datetime.now() - timedelta(days = 1)
            news_date = news_date.strftime('%Y-%m-%d')
            news['date'] = datetime.strptime(news_date + ' ' + news_time, '%Y-%m-%d %H:%M')
        else:
            news_date = news_datetime.replace('\xa0в', '')
            for old, new in [('\xa0января', '-01-'), ('\xa0февраля', '-02-'), ('\xa0марта', '-03-'), ('\xa0апреля', '-04-'), ('\xa0мая', '-05-'), ('\xa0июня', '-06-'), ('\xa0июля', '-07-'), ('\xa0августа', '-08-'), ('\xa0сентября', '-09-'), ('\xa0октября', '-10-'), ('\xa0ноября', '-11-'), ('\xa0декабря', '-12-')]:
                news_date = news_date.replace(old, new)
            news['date'] = datetime.strptime(news_date[:-1]+ str(datetime.now().year), '%d-%m-%Y')

        news['url'] = str(block.xpath(".//h2[@class='story__title']/a/@href")[0])
        news['url'] = yandex_main_url + news['url'][: news['url'].find('?')]
        news['src'] = str(get_response(news['url']).xpath("//a[contains(text(),'источник')]/@href | //div[text()='Читать в источнике']/../@href")[0])
        yandex_news.append(news)
    return yandex_news

def insert_new_data(data, collection):
    for itm in data:
        collection.update_one({'url': itm['url']}, {'$set': itm}, upsert = True)

client = MongoClient('localhost', 27017)
db = client['news_db']


lenta = lenta_news()
mail = mail_news()
yandex = yandex_news()

insert_new_data(lenta, db.lenta)
insert_new_data(mail, db.mail)
insert_new_data(yandex, db.yandex)