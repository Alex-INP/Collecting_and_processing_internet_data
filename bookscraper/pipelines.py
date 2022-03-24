# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
import re
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class BookscraperPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.database = client["books_db"]

    def process_item(self, item, spider):
        cursor = self.database[spider.name]

        self.correct_name(item)
        self.correct_authors(item)
        self.correct_prices(item)
        self.correct_rating(item)

        cursor.insert_one(dict(item))

    def correct_name(self, item):
        if item["authors"] is not None:
            item["name"] = ":".join(item["name"].split(":")[1:])

        if item["name"][0] == " ":
            item["name"] = item["name"][1:]
        if item["name"][-1] == " ":
            item["name"] = item["name"][:-1]

    def correct_authors(self, item):
        if item["authors"] is not None:
            if len(item["authors"]) != 1:
                item["authors"] = ", ".join(
                    list(filter(lambda x: x != ", ", item["authors"])))
            else:
                item["authors"] = item["authors"][0]

            if item["authors"][0] == " ":
                item["authors"] = item["authors"][1:]
            if item["authors"][-1] == " ":
                item["authors"] = item["authors"][:-1]

    def correct_prices(self, item):
        if item["price"] is not None:
            if item["price"][0] == " ":
                item["price"] = item["price"][1:]
            if item["price"][-1] == " ":
                item["price"] = item["price"][:-1]

            item["price"] = item["price"].replace("\xa0", "")
            if item["price"][-1] == "₽":
                item["price"] = item["price"][:-2]

        if item["discount_price"] is not None:
            if item["discount_price"][0] == " ":
                item["discount_price"] = item["discount_price"][1:]
            if item["price"][-1] == " ":
                item["discount_price"] = item["discount_price"][:-1]
            item["discount_price"] = item["discount_price"].replace(r"\xa0", " ")

    def correct_rating(self, item):
        if item["rating"] is not None:
            if item["rating"][0] == " ":
                item["rating"] = item["rating"][1:]
            if item["rating"][-1] == " ":
                item["rating"] = item["rating"][:-1]


class LeroyParserPipeline:
    def process_item(self, item, spider):
        return item


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item["pictures"]:
            for ind, p_link in enumerate(item["pictures"]):
                width = self.get_position_data("w_82", p_link)
                p_link = p_link.replace(p_link[width[0]:width[1]], "w_2000")

                height = self.get_position_data("h_82", p_link)
                p_link = p_link.replace(p_link[height[0]:height[1]], "h_2000")

                item["pictures"][ind] = p_link

                for link in item["pictures"]:
                    try:
                        yield scrapy.Request(link)
                    except Exception as e:
                        print(e)

    def item_completed(self, results, item, info):
        item["pictures"] = [i[1] for i in results if i[0]]
        return item

    def get_position_data(self, segment, full_text):
        result = re.search(fr"{segment}", full_text)
        return [result.start(), result.end()]
