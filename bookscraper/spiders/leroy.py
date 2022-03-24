import sys
sys.path.append("../")

import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader

from bookscraper.items import LeroyscraperItem

class LeroySpider(scrapy.Spider):
    name = 'leroy'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/search/?q=%D0%BF%D0%BB%D0%B8%D1%82%D0%BA%D0%B0']

    def parse(self, response: HtmlResponse):
        links = response.css("a[data-qa='product-image']")
        for link in links:
            yield response.follow(link, callback=self.process_page)

    def process_page(self, response):
        loader = ItemLoader(item=LeroyscraperItem(), response=response)
        loader.add_css("name", "h1::text")
        loader.add_css("price", "span[slot='price']::text")
        loader.add_value("link", response.url)
        loader.add_css("pictures", "img[slot='thumbs']::attr(src)")

        yield loader.load_item()



