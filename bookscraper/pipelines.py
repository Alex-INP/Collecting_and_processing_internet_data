# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


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

