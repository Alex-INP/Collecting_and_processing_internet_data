from lxml import html
import requests
from pprint import pprint

from pymongo import MongoClient


def get_news_data(news_list, headers):
	result_data = []
	for url in news_list:
		news_dict = {"source": None,
					 "name": None,
					 "link": url,
					 "date": None,
					 "time": None}
		response = requests.get(url, headers=headers)
		document = html.fromstring(response.text)
		news_dict["name"] = document.xpath("//h1/text()")[0]
		news_dict["date"], news_dict["time"] = document.xpath(
			"//span[contains(@class, 'note__text breadcrumbs__text js-ago')]/@datetime")[0].split("T")
		news_dict["source"] = document.xpath("//span[@class='note']/a/span/text()")[0]
		result_data.append(news_dict)
	return result_data


def add_to_db(news_data):
	mongo_client = MongoClient("localhost", 27017)
	database = mongo_client["news_database"]

	news_cursor = database.news
	news_cursor.delete_many({})

	for i in news_data:
		news_cursor.insert_one(i)

	for i in news_cursor.find({}):
		print("-"*150)
		print(i)


def main():
	url = "https://news.mail.ru/?_ga=2.52001898.2107162005.1645944815-1292694162.1644053642"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
	response = requests.get(url, headers=headers)
	document = html.fromstring(response.text)
	links = document.xpath("//ul[@data-module='TrackBlocks']/li[@class='list__item']//@href")

	scraped_news = get_news_data(links, headers)
	pprint(scraped_news, sort_dicts=False)

	add_to_db(scraped_news)


if __name__ == "__main__":
	main()
