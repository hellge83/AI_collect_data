# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:16:48 2020

@author: snetkova
"""
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings

from leroymerlin.spiders.leroy import LeroySpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings = crawler_settings)
    process.crawl(LeroySpider, search = 'краска')
    process.start()
