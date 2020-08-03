import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://kaliningrad.hh.ru/search/vacancy?L_save_area=true&clusters=true&enable_snippets=true&search_field=name&text=%D0%B0%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&showClusters=true']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'HH-Pager-Controls-Next')]/@href").extract_first()
        
        yield response.follow(next_page, callback = self.parse)
        vacancy_links = response.xpath("//a[contains(@class, 'HH-LinkModifier')]/@href").extract()
        
        for link in vacancy_links:
            yield response.follow(link, callback = self.vacancy_parse)
            
            
    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p[@class = 'vacancy-salary']/span/text()").extract()
        url = response.url
        
        yield JobparserItem(item_name = name, item_salary = salary, item_url = url)
        # print(f'NXT_PG {salary}')
        # pass


