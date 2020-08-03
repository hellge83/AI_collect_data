import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/analitik.html?profession_only=1&noGeo=1']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").extract_first()
        
        yield response.follow(next_page, callback = self.parse)
        vacancy_links = response.xpath("//div[@class='_3mfro PlM3e _2JVkc _3LJqf']/a/@href").extract()
        
        for link in vacancy_links:
            yield response.follow(link, callback = self.vacancy_parse)
            
            
    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        url = response.url
        
        yield JobparserItem(item_name = name, item_salary = salary, item_url = url)
        # print(f'NXT_PG {url}')
        # pass
