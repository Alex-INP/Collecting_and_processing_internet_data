import json
from pymongo import MongoClient


def add_unique_vacancy(cursor, data):
	if not cursor.find_one(data):
		cursor.insert_one(data)


def main():
	mongo_client = MongoClient("localhost", 27017)
	database = mongo_client["vacancy_database"]

	vacancy_cursor = database.vacancy

	vacancy_cursor.delete_many({})

	with open("scrap_result.txt", "r", encoding="utf-8") as file:
		content = json.load(file)
	data_content = []
	for page in content:
		data_list = page["данные"]
		for data in data_list:
			data["зарплата"]["от"] = data["зарплата"]["от"]
			data["зарплата"]["до"] = data["зарплата"]["до"]
			data_content.append(data)

	for data in data_content:
		add_unique_vacancy(vacancy_cursor, data)

	for i in vacancy_cursor.find({}):
		print(i)


if __name__ == "__main__":
	main()
