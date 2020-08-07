import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader

class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']
    
    def __init__(self, search):
        super().__init__()
        self.start_urls = [f'http://leroymerlin.ru/search/?q={search}']
                           

    def parse(self, response: HtmlResponse):
        # reverse comment to parse all available pages 
        # next_page = response.xpath("//a[contains(@class, 'next-paginator-button')]/@href").extract_first()
        # yield response.follow(next_page, callback = self.parse)

        itm_links = response.xpath("//uc-plp-item-new/@href")
        for link in itm_links:
            yield response.follow(link, callback = self.itm_parse)
            
    def itm_parse(self, response: HtmlResponse):
        loader = ItemLoader(item = LeroymerlinItem(), response = response)
        loader.add_xpath('name',"//h1/text()")
        loader.add_xpath('photos',"//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('_id',"//span[@slot='article']/@content")
        loader.add_xpath('price',"//uc-pdp-price-view[@slot='primary-price']/meta[@itemprop='price']/@content")
        loader.add_xpath('info',"//div[@class='def-list__group']")
        # loader.add_css()
        loader.add_value('url', response.url)
        yield loader.load_item()