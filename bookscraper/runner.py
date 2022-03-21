import sys

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

import settings
from spiders.book24 import Book24Spider


if __name__ == '__main__':
    sys.path.append("../")

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(Book24Spider)

    crawler_process.start()
