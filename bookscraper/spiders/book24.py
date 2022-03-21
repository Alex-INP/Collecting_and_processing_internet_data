import sys

import scrapy
from scrapy.http import HtmlResponse

sys.path.append("../")
from bookscraper.items import BookscraperItem

class Book24Spider(scrapy.Spider):
    name = "book24"
    allowed_domains = ["book24.ru"]
    start_urls = ["https://book24.ru/search/?q=Python"]

    def parse(self, response: HtmlResponse):
        try:
            page = response.meta["page"]
            yield response.follow(f"https://book24.ru/search/page-{page}/?q=Python",
                            callback=self.parse, meta={"page": page+1})
        except KeyError:
            yield response.follow(f"https://book24.ru/search/page-2/?q=Python",
                            callback=self.parse, meta={"page": 3})

        links = response.css("a.product-card__image-link.smartLink::attr(href)").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_link)

    def parse_link(self, response):
        result = {
            "name": None,
            "link": response.url,
            "authors": None,
            "price": None,
            "discount_price": None,
            "rating": None
        }
        book_data = response.css("ul.product-characteristic__list")
        author_el = book_data.css("div.product-characteristic__item")[0]

        if author_el.css("span.product-characteristic__label::text").get() == " Автор: ":
            result["authors"] = author_el.xpath("./div[@class='product-characteristic__value']//text()").getall()
        result["name"] = response.css("h1.product-detail-page__title::text").get()

        result["price"] = response.css("span.app-price.product-sidebar-price__price").css("meta[itemprop='price']::attr(content)").get()
        if pre_discount_price := response.css("span.app-price.product-sidebar-price__price-old::text").get():
            result["discount_price"] = result["price"]
            result["price"] = pre_discount_price

        result["rating"] = response.xpath(
            "//div/span[contains(text(), ' Возрастное ограничение: ')]/../../div[@class='product-characteristic__value']//text()"
        ).get()

        yield BookscraperItem(**result)





